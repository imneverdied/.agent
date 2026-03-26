---
name: ffmpeg
description: Use the bundled ffmpeg.exe in this skill folder for all video/audio processing. Do not require global ffmpeg installation.
metadata: {"openclaw":{"emoji":"video","requires":{"bins":[]}},"clawdbot":{"emoji":"video","requires":{"bins":[]},"os":["win32"]}}
---

# FFmpeg (Bundled EXE Only)

This skill ships with a local executable:

- Windows EXE path: `.agent/skills/ffmpeg/ffmpeg.exe`

## Mandatory Execution Rule

- Always call the bundled EXE in this folder.
- Do not call plain `ffmpeg` from PATH.
- Do not ask user to install ffmpeg globally.
- If `.agent/skills/ffmpeg/ffmpeg.exe` is missing, stop and tell the user:
  "在 `.agent/skills/ffmpeg/` 找不到 `ffmpeg.exe`，請先放入 `ffmpeg.exe` 後再繼續。"

## Command Templates

PowerShell:

```powershell
& ".\.agent\skills\ffmpeg\ffmpeg.exe" -version
```

CMD:

```bat
".\.agent\skills\ffmpeg\ffmpeg.exe" -version
```

## Quick Safety Check Before Work

```powershell
if (!(Test-Path ".\.agent\skills\ffmpeg\ffmpeg.exe")) {
  throw "在 .agent/skills/ffmpeg/ 找不到 ffmpeg.exe，請先放入 ffmpeg.exe 後再繼續。"
}
```

## Common Examples (Using Bundled EXE)

Trim 10s from 00:00:30:

```powershell
& ".\.agent\skills\ffmpeg\ffmpeg.exe" -ss 00:00:30 -i "input.mp4" -t 10 -c copy "clip.mp4" -y
```

Convert to H.264 + AAC:

```powershell
& ".\.agent\skills\ffmpeg\ffmpeg.exe" -i "input.mov" -c:v libx264 -crf 20 -preset medium -c:a aac -b:a 192k "output.mp4" -y
```

Extract audio only:

```powershell
& ".\.agent\skills\ffmpeg\ffmpeg.exe" -i "input.mp4" -vn -c:a aac -b:a 192k "audio.m4a" -y
```

Burn subtitles:

```powershell
& ".\.agent\skills\ffmpeg\ffmpeg.exe" -i "input.mp4" -vf "subtitles=subs.srt" -c:v libx264 -crf 20 -c:a copy "subbed.mp4" -y
```

## Notes

- `-ss` before `-i` is faster seek; after `-i` is more accurate.
- `-c copy` is stream copy (no re-encode).
- Filters require re-encoding (cannot combine filter with full stream copy).
