# SHAH Group AI OS — Installation Guide

**Version**: 2.0 (Post-Phase-2)  
**OS**: Windows 11  
**Server**: Local — http://127.0.0.1:8899/

---

## Prerequisites

Before starting, ensure the following are available on your machine:

| Requirement | Version | Check Command | Required? |
|-------------|---------|---------------|-----------|
| Python | 3.11+ | `python --version` | **YES** |
| Git | Any | `git --version` | YES (repo management) |
| Node.js | 16+ | `node --version` | Optional (browser tests only) |
| FFmpeg | Any | `ffmpeg -version` | Optional (Reel Studio only) |

> [!NOTE]
> The existing development environment uses the Hermes-bundled Python at:  
> `C:\Users\HP\AppData\Local\hermes\tools\python-3.14.9+20261021-win32-x64\python.exe`  
> You can use any Python 3.11+ interpreter instead.

---

## Step 1 — Get the Project

### Option A: Clone from GitHub
```powershell
git clone https://github.com/abhi23122001/ssc_marketing_managing.git
cd ssc_marketing_managing
```

### Option B: Use Existing Local Copy
The project already exists at:
```
C:\Users\HP\Desktop\ssc_marketing_managing
```
No cloning needed if working on the same machine.

---

## Step 2 — Verify Python

```powershell
# Check Python is available
python --version

# Or use the Hermes-bundled Python
C:\Users\HP\AppData\Local\hermes\tools\python-3.14.9+20261021-win32-x64\python.exe --version
```

The application uses **Python standard library only** for the server.  
No `pip install` is required for core functionality.

---

## Step 3 — Verify the Database

The database file should already exist:
```powershell
Test-Path "C:\Users\HP\Desktop\ssc_marketing_managing\data\sgcc_foundation.sqlite"
```

If it's missing, run the migration:
```powershell
cd "C:\Users\HP\Desktop\ssc_marketing_managing"
python foundation/domains/migrate.py
```

---

## Step 4 — Start the Server

### Quick Start (foreground)
```powershell
cd "C:\Users\HP\Desktop\ssc_marketing_managing"
python foundation/api.py
```

You should see:
```
SHAI foundation API listening on http://127.0.0.1:8899
```

### Background Start (PowerShell)
```powershell
cd "C:\Users\HP\Desktop\ssc_marketing_managing"
Start-Process -FilePath "python" -ArgumentList "foundation/api.py" -WindowStyle Hidden
```

### Using the Hermes Python (exact binary)
```powershell
cd "C:\Users\HP\Desktop\ssc_marketing_managing"
C:\Users\HP\AppData\Local\hermes\tools\python-3.14.9+20261021-win32-x64\python.exe foundation/api.py
```

---

## Step 5 — Open the Dashboard

Open your web browser and navigate to:
```
http://127.0.0.1:8899/
```

---

## Step 6 — Log In

Use one of the demo credentials:

| Username | Password | Role | Workspace |
|----------|----------|------|-----------|
| `owner` | `demo-owner-pass-0001` | Owner (all access) | SSC |
| `manager` | `demo-manager-pass-0001` | Manager | SSC |
| `employee` | `demo-employee-pass-0001` | Employee | SSC |
| `finance` | `demo-finance-pass-0001` | Finance Manager | INFRA |
| `pm` | `demo-pm-pass-0001` | Project Manager | INFRA |
| `viewer` | `demo-viewer-pass-0001` | Viewer | INFRA |

> [!CAUTION]
> Change all demo passwords before using in production or sharing access.

---

## Step 7 — Verify the Installation

Run the foundation test battery:
```powershell
cd "C:\Users\HP\Desktop\ssc_marketing_managing"
python foundation/tests/run_foundation_tests.py
```

Expected output:
```
47/47 tests passed
```

Run the live API test (requires server running on 8899):
```powershell
python tmp_full_api_test.py
```

Expected output:
```
55/55 checks PASS
```

---

## Stopping the Server

If running in the foreground: press `Ctrl+C`

If running as background process:
```powershell
Get-Process -Name "python" | Where-Object { $_.MainWindowTitle -eq "" } | Stop-Process
```

---

## Configuration

The server configuration is in `foundation/config.py` and reads from `config/settings.json` (if present).

Default configuration:
```json
{
  "host": "127.0.0.1",
  "port": 8899,
  "db": "data/sgcc_foundation.sqlite"
}
```

To change the port, edit `config/settings.json`:
```json
{
  "port": 8080
}
```

---

## Backup

Create a manual backup at any time:
```powershell
cd "C:\Users\HP\Desktop\ssc_marketing_managing"
.\Start-SHAI-Backup.ps1
```

Backups are stored in the `backups/` directory with timestamp-based names.

---

## Restore from Backup

```powershell
cd "C:\Users\HP\Desktop\ssc_marketing_managing"
.\Start-SHAI-Restore-Test.ps1
```

---

## Troubleshooting

### Server won't start — port 8899 already in use
```powershell
# Find and kill the process using port 8899
netstat -ano | findstr :8899
taskkill /PID <PID> /F
```

### Database locked error
```powershell
# Close all Python processes
Get-Process python | Stop-Process -Force
# Then restart the server
python foundation/api.py
```

### Login fails (401)
- Verify the username and password from the table above
- Check that the server is running (`http://127.0.0.1:8899/api/health`)
- If the server responds with 404 on `/api/health`, use `/health` instead

### Missing Python modules
The application uses stdlib only. If you see `ModuleNotFoundError`:
```powershell
# Install psutil (optional — for system health metrics only)
pip install psutil
```

---

## Production Deployment Checklist

Before moving from local to production:

- [ ] Change all 6 demo account passwords
- [ ] Add HTTPS via nginx reverse proxy + Let's Encrypt
- [ ] Set `host = "0.0.0.0"` in config (or keep `127.0.0.1` for nginx-proxied setup)
- [ ] Add Windows Firewall rules
- [ ] Set up automated backup via Windows Task Scheduler
- [ ] Remove or disable test/tmp files from project root
- [ ] Review `SECURITY_AUDIT.md` and address all HIGH severity items

---

*Last updated: 2026-11-20*
