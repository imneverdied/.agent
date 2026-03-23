---
name: project-context
description: 專案背景知識、交接規範與本機工作狀態初始化。當任務涉及文件維護、流程調整、資料處理、跨回合交接，或在新電腦 / fresh clone 接手此專案時使用；先檢查 `.agent/skills/project-context` 狀態檔是否存在，必要時執行 `.agent/init.ps1`，再讀 AGENTS、HEARTBEAT、STATUS 與 SQLite 紀錄。
---

# Project Context

## 啟動步驟
每次開始新對話或接到任務時，依序執行：

### Step 0：確認 project-context 是否已初始化
- 檢查以下檔案是否存在：
  - `.agent/skills/project-context/STATUS.md`
  - `.agent/skills/project-context/backup_log.db`
- 若任一缺失，在專案根目錄先執行：

```powershell
powershell -ExecutionPolicy Bypass -File .agent/init.ps1
```

- 視為正常情況：`STATUS.md` 與 `backup_log.db` 可能被 `.gitignore` 忽略，所以新電腦 fresh clone 不一定會自帶。

### Step 1：讀取目前狀態
- 先讀 `.agent/skills/project-context/STATUS.md`
- 先確認：上一輪目標、已改檔案、未完成事項、下一步。
- 再讀 SQLite 紀錄：
  - 最近紀錄：`python .agent/skills/project-context/scripts/backup_db_read.py --limit 20`
  - 單筆詳情：`python .agent/skills/project-context/scripts/backup_db_read.py --event-id <id> --as-json`

### Step 2：讀取專案入口文件
- 先讀專案根目錄 `AGENTS.md`（若存在）。
- 再讀專案根目錄 `HEARTBEAT.md`（若存在）。
- 再讀 `.agent/README.md`（若存在）。
- 最後才讀各子資料夾 README（若存在）。
- 若根目錄沒有 `README.md`，不要視為異常。
- 建議指令：
  - `rg --files -g "AGENTS.md" -g "HEARTBEAT.md" -g "*README*.md" .`

### Step 3：讀取本地設定檔
- 掃描 `.env` / `.env.*`（若存在）。
- 優先檢查：
  - `.agent/.env`
  - `bot/backend/.env`
  - `bot/backend/.env.example`
  - `bot/frontend/.env.local`
  - `bot/frontend/.env.local.example`
- 只記錄必要設定名稱，不在輸出中暴露密碼或 token。

### Step 4：確認本回合關鍵產物
- 依當前任務列出「必須更新」與「不可破壞」檔案。
- 實作前先確認輸入來源，實作後確認輸出產物存在且可讀。
- 對於新電腦或空工作區，要先分辨哪些是可重建的本機產物：
  - 可重建：`.venv`、`node_modules`、`.next`、log、`bot/backend/data/uploads`、`bot/backend/data/chroma`
  - 需手動補齊：`.agent/.env`、`bot/frontend/.env.local`、NotebookLM 登入狀態

## 強制規則

### A. 編輯前先備份
- 任何既有檔案修改前，先備份到同資料夾 `backup/`。
- 備份命名建議：`原檔名.bak_YYYYMMDD_HHMMSS`。

### B. 每次對話結束都更新 STATUS
- 必須更新：`.agent/skills/project-context/STATUS.md`
- 至少填：Goal / Changes / Decisions / Risks / Next / Repo changes。
- 若無寫入，仍要記：`No repo changes`。

### C. 每次對話結束都寫入 SQLite 紀錄
- 寫入腳本：`backup_db_write.py`
- 讀取腳本：`backup_db_read.py`
- 最低要求：每回合至少一筆 `backup_events`。
- 若 DB 尚未建立，先回到 Step 0 執行 `.agent/init.ps1`。

## SQLite 紀錄實作（project-context）
- DB：`.agent/skills/project-context/backup_log.db`
- 寫入腳本：`.agent/skills/project-context/scripts/backup_db_write.py`
- 讀取腳本：`.agent/skills/project-context/scripts/backup_db_read.py`

最小寫入範例：
```bash
python .agent/skills/project-context/scripts/backup_db_write.py \
  --summary "Update docs" \
  --source codex \
  --repo-changes yes \
  --item ".agent/skills/project-context/SKILL.md|.agent/skills/project-context/backup/SKILL.md.bak_YYYYMMDD_HHMMSS|update"
```

## 任務交接摘要（建議）
- 目前目標：一句話描述本回合要完成的事。
- 變更檔案：列出主要檔案與用途。
- 風險與阻塞：列出仍未解決項目。
- 下一步：給下一位 agent 的最短可執行行動。

## 注意事項
- 優先使用繁體中文。
- 新增規則與流程改動要同時更新 `SKILL.md`、`STATUS.md`、SQLite 紀錄。
- 不要假設狀態檔、SQLite、`.env.local` 或 `.agent/.env` 一定已被版控；先檢查，缺失時先初始化或提示補齊。
- 如有 `.agent/workflows/`，可配合使用。
