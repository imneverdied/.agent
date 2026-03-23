# .agent

這個資料夾現在是乾淨的本地 agent 工作區。

目前保留的是可重用的 skill 套件與 archive，已清空舊專案記憶，不包含先前工作狀態、備份紀錄或本機 API 設定。

## 結構

- `skills/`: 啟用中的 skills
- `skill-archives/`: 保留用的 skill 歷史版本
- `init.ps1`: 重新建立空白 `project-context` 狀態
- `.env`: 本機環境變數範本

## 初始化

如果你要重新建立空白的 `project-context` 狀態，可以執行：

```powershell
powershell -ExecutionPolicy Bypass -File .agent/init.ps1
```

如果你目前就在 `.agent` 資料夾內，也可以直接執行：

```powershell
powershell -ExecutionPolicy Bypass -File .\init.ps1
```
