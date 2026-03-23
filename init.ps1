$ErrorActionPreference = "Stop"

function Get-AgentRoot {
    $cwd = (Get-Location).Path
    $agentFromProjectRoot = Join-Path $cwd ".agent"

    if (Test-Path $agentFromProjectRoot) {
        return $agentFromProjectRoot
    }

    return $cwd
}

function Test-CommandExists {
    param([Parameter(Mandatory = $true)][string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

$agentRoot = Get-AgentRoot
$projectContextDir = Join-Path $agentRoot "skills\project-context"
$statusPath = Join-Path $projectContextDir "STATUS.md"
$backupDir = Join-Path $projectContextDir "backup"
$dbPath = Join-Path $projectContextDir "backup_log.db"

Write-Host "[init] Agent root: $agentRoot"

if (-not (Test-Path $projectContextDir)) {
    throw "[init] Missing directory: $projectContextDir"
}

if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Write-Host "[init] Created backup directory"
}

@"
# Project Status

## Current State
- Fresh workspace.
- No project memory yet.
- Add a new entry below when work starts.

## Entry Template
### YYYY-MM-DD HH:MM
- Goal:
- Changes:
- Decisions/Assumptions:
- Risks/Blockers:
- Next:
- Repo changes: Yes/No
"@ | Set-Content -Encoding utf8 $statusPath

Write-Host "[init] Reset STATUS.md"

if (Test-Path $dbPath) {
    Remove-Item -Force $dbPath
    Write-Host "[init] Removed existing backup_log.db"
}

$dbSchema = @"
CREATE TABLE IF NOT EXISTS backup_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    source TEXT NOT NULL,
    summary TEXT NOT NULL,
    repo_changes INTEGER NOT NULL CHECK (repo_changes IN (0,1)),
    note TEXT
);

CREATE TABLE IF NOT EXISTS backup_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    backup_path TEXT,
    action TEXT NOT NULL DEFAULT 'update',
    file_hash TEXT,
    file_size INTEGER,
    FOREIGN KEY(event_id) REFERENCES backup_events(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_backup_events_created_at
    ON backup_events(created_at);
CREATE INDEX IF NOT EXISTS idx_backup_files_event_id
    ON backup_files(event_id);
"@

if (Test-CommandExists -Name "python") {
    $env:AGENT_DB_PATH = $dbPath
    $env:AGENT_DB_SCHEMA = $dbSchema
    & python -c "import os, sqlite3; conn = sqlite3.connect(os.environ['AGENT_DB_PATH']); conn.executescript(os.environ['AGENT_DB_SCHEMA']); conn.close()"

    if ($LASTEXITCODE -ne 0) {
        throw "[init] Failed to create backup_log.db schema"
    }

    Write-Host "[init] Created empty backup_log.db"
}
else {
    Write-Host "[warn] Python not found; backup_log.db was not created."
}

Write-Host "[ok] .agent reset completed."
