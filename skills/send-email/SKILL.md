---
name: send-email
description: Send emails via SMTP. Configure in ~/.openclaw/openclaw.json under skills.entries.send-email.env.
metadata: {"openclaw":{"emoji":"mail","requires":{"anyBins":["python","python3"]}}}
---

# Send Email

Send emails via the Python script. SMTP settings are injected by OpenClaw runtime (`~/.openclaw/openclaw.json` -> `skills.entries.send-email.env`).

## Configuration

Configure in `~/.openclaw/openclaw.json`:

```json
"skills": {
  "entries": {
    "send-email": {
      "enabled": true,
      "env": {
        "EMAIL_SMTP_SERVER": "smtp.example.com",
        "EMAIL_SMTP_PORT": "465",
        "EMAIL_SENDER": "your-email@example.com",
        "EMAIL_SMTP_PASSWORD": "YOUR_AUTH_CODE"
      }
    }
  }
}
```

## Agent Instructions

1. Do not read credential config files in tool output.
2. Send email from this workspace path:
   - `python .agent/skills/send-email/send_email.py "recipient" "Subject" "Body"`
3. With attachment:
   - `python .agent/skills/send-email/send_email.py "recipient" "Subject" "Body" "path/to/file.pdf"`

## Examples

```bash
python .agent/skills/send-email/send_email.py "recipient@example.com" "Subject" "Body text"
python .agent/skills/send-email/send_email.py "recipient@example.com" "Subject" "Body" "path/to/file.pdf"
```
