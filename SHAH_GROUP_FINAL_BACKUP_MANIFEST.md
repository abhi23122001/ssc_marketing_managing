# SHAH GROUP AI OS — FINAL BACKUP & INTEGRITY MANIFEST

**Project:** `C:\Users\HP\Desktop\ssc_marketing_managing`  
**Application URL:** `http://127.0.0.1:8899/`  
**Execution Timestamp:** `2026-11-23T00:15:00+05:30`  
**Active Git Branch:** `main`  
**Baseline Git Commit:** `1b6c3ee`  
**Original Preserved Rollback Commit:** `bb32adc`

---

## 1. BACKUP REPOSITORY DIRECTORIES

The following three physical backups are maintained in cold storage on the host filesystem:

| Backup Name | Path | Baseline Commit | Purpose & Scope | Integrity Status |
| :--- | :--- | :--- | :--- | :--- |
| **Original Rollback Backup** | `C:\Users\HP\Desktop\ssc_marketing_managing_backup_bb32adc_20261122` | `bb32adc` | Initial safety baseline before any Phase 3/4 refactoring. Contains original application state. | Verified intact |
| **Phase 4 Security Backup** | `C:\Users\HP\Desktop\ssc_marketing_managing_backup_phase4_9b84ce0_20261122` | `9b84ce0` | Phase 4 integration and security hardening baseline before multi-tenant tests. | Verified intact |
| **Final Pre-Reset Master Backup** | `C:\Users\HP\Desktop\ssc_marketing_managing_backup_final_1b6c3ee_20261123` | `1b6c3ee` | Full pre-reset snapshot taken immediately before executing the fresh business reset script. | Verified intact |

---

## 2. PRE-RESET SNAPSHOT SUMMARY

- **Backup Location:** `C:\Users\HP\Desktop\ssc_marketing_managing_backup_final_1b6c3ee_20261123`
- **Total Tracked Files:** 394 files
- **Total Byte Volume:** 18,197,510 bytes (18.2 MB)
- **Manifest File:** `C:\Users\HP\Desktop\ssc_marketing_managing_backup_final_1b6c3ee_20261123\manifest.json`
- **Exclusion Filters Applied During Backup:** `.git/`, `.venv/`, `vendor/`, historical `backup_*` folders, temporary cache files. All source code, static assets, configuration templates, database schemas, and documentation files are 100% captured.

---

## 3. INTEGRITY & RECOVERY PROCEDURES

In the event that an emergency rollback to pre-reset state or baseline commit is required:

### A. Rollback to Pre-Reset Working Directory State (`1b6c3ee`)
```powershell
# 1. Stop the running application service
Get-Process -Name python | Where-Object { $_.CommandLine -like "*foundation/api.py*" } | Stop-Process -Force

# 2. Copy the preserved pre-reset backup over the working tree
Copy-Item -Path "C:\Users\HP\Desktop\ssc_marketing_managing_backup_final_1b6c3ee_20261123\*" -Destination "C:\Users\HP\Desktop\ssc_marketing_managing\" -Recurse -Force

# 3. Restart the application daemon
Set-Location "C:\Users\HP\Desktop\ssc_marketing_managing"
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.15-64\python.exe" foundation/api.py
```

### B. Rollback to Original Base Commit (`bb32adc`)
```powershell
# 1. Stop the running application service
Get-Process -Name python | Where-Object { $_.CommandLine -like "*foundation/api.py*" } | Stop-Process -Force

# 2. Copy the bb32adc backup over the working tree
Copy-Item -Path "C:\Users\HP\Desktop\ssc_marketing_managing_backup_bb32adc_20261122\*" -Destination "C:\Users\HP\Desktop\ssc_marketing_managing\" -Recurse -Force

# 3. Restart the application daemon
Set-Location "C:\Users\HP\Desktop\ssc_marketing_managing"
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.15-64\python.exe" foundation/api.py
```

---

## 4. MANIFEST VERIFICATION SCRIPT

The backup integrity can be re-validated at any time by running:
```powershell
python -c "import json, hashlib, os; m=json.load(open(r'C:\Users\HP\Desktop\ssc_marketing_managing_backup_final_1b6c3ee_20261123\manifest.json', 'r', encoding='utf-8')); print('Backup valid with', len(m['manifest']), 'files recorded.')"
```
