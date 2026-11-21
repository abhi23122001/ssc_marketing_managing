# SHAH GROUP AI OS — HOST MACHINE SHUTDOWN LIMITATIONS & VPS HOSTING BLUEPRINT

## 1. EXECUTIVE SUMMARY & LOCAL ARCHITECTURE

The SHAH Group AI Operating System currently executes as a local-first, zero-paid-dependency application on the owner's Windows workstation:
- **Application URL**: `http://127.0.0.1:8899/`
- **Backend**: Python 3.15 standard library HTTP server (`foundation/api.py`)
- **Database**: SQLite WAL mode in `data/sgcc_foundation.sqlite` (73 tables)
- **Local AI Orchestration**: Hermes Agent CLI (`v0.23.1`) + Nous Research OAuth Free Inference (`upstage/solar-mini4:free`, `stepfun/step-3.7-flash:free`)
- **Video & Graphics Engine**: Local FFmpeg (`9.0.2-full_build-www.gyan.dev`) + HTML5 Canvas
- **Background Daemon**: In-process threading scheduler (`foundation/domains/ai_scheduler.py`) operating in the `Asia/Kolkata` (IST) timezone.

---

## 2. LOCAL HOST MACHINE SHUTDOWN LIMITATION

### 2.1 The Technical Limitation
When running natively on a Windows laptop or desktop workstation:
1. **Machine Power Off / Hibernate / Sleep**: When the host machine is turned off, put to sleep, or disconnected from power, the operating system halts all userland processes. The Python server, background scheduler daemon, and Hermes CLI process suspend execution.
2. **Scheduled Job Deferral**: Any cron/scheduler tasks scheduled during the sleep period (e.g., Morning 07:00 AM Marketing Briefs or 08:00 AM Daily Research) cannot fire while the CPU is powered off.
3. **Catch-up Architecture**: Upon system restart, `AutonomousDaemon` immediately detects missed schedules, executes the pending daily tasks, and logs the execution to `ai_scheduler_runs`.

### 2.2 Operational Guidance for Windows Workstation
- If 24/7 continuous autonomous posting or midnight database snapshots are desired while keeping the system on the local workstation:
  - Disable Windows Automatic Sleep under **Power & Sleep Settings** when plugged into AC power.
  - Enable **Start-SHAI-Center.ps1** in Windows Task Scheduler on system boot.

---

## 3. PRODUCTION 24/7 VPS DEPLOYMENT BLUEPRINT

To achieve 100% continuous 24/7/365 uptime, eliminate machine sleep constraints, and allow multi-user remote access for field engineers across Nagpur and project sites:

### 3.1 Recommended Infrastructure
- **Server**: Lightweight Linux VPS (Ubuntu 22.04 LTS or 24.04 LTS)
- **Providers**: Hetzner Cloud (CX22 ~€3.79/mo), DigitalOcean Droplet ($4–$6/mo), Linode, or AWS EC2 `t4g.small`
- **Specs**: 2 vCPU, 2 GB RAM, 40 GB NVMe SSD (sufficient for entire OS, SQLite DB, FFmpeg renders, and model caching).

### 3.2 Deployment Steps

#### Step 1: Base Packages
```bash
sudo apt update && sudo apt install -y python3 python3-pip ffmpeg nginx git certbot python3-certbot-nginx
```

#### Step 2: Clone Repository & Setup Directory
```bash
sudo mkdir -p /opt/shah_group_ai_os
sudo chown -R $USER:$USER /opt/shah_group_ai_os
cd /opt/shah_group_ai_os
# Restore latest milestone backup or clone git repo
cp -r /path/to/backup/* .
```

#### Step 3: Install Hermes Agent CLI on Linux (Zero Paid Dependency)
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/install.sh | bash
# Copy existing nous oauth credentials from Windows %LOCALAPPDATA%\hermes\auth.json to ~/.hermes/auth.json
```

#### Step 4: Configure systemd 24/7 Background Service
Create `/etc/systemd/system/shah-ai-os.service`:
```ini
[Unit]
Description=SHAH Group AI Operating System Backend & Scheduler
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/shah_group_ai_os
ExecStart=/usr/bin/python3 foundation/api.py
Restart=always
RestartSec=5
Environment=PORT=8899
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```
Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable shah-ai-os
sudo systemctl start shah-ai-os
sudo systemctl status shah-ai-os
```

#### Step 5: Nginx Reverse Proxy with Free Let's Encrypt SSL
Create `/etc/nginx/sites-available/shah-ai-os`:
```nginx
server {
    server_name os.shahgroup.in;

    location / {
        proxy_pass http://127.0.0.1:8899;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 50M;
}
```
Enable site and generate SSL:
```bash
sudo ln -s /etc/nginx/sites-available/shah-ai-os /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d os.shahgroup.in --non-interactive --agree-tos -m admin@shahgroup.in
```

---

## 4. SECURITY & DATA BACKUP PERSISTENCE ON VPS

1. **Automated Remote Backups**:
   - A daily cron job executes `python scripts/create_creative_studio_complete_backup.py`.
   - SQLite `VACUUM INTO` creates clean point-in-time snapshots without locking writes.
2. **Access Control**:
   - Nginx handles TLS 1.3 encryption.
   - Built-in multi-tenant RBAC strictly isolates SSC and INFRA workspaces.
   - Zero external cloud database dependencies; full ownership of data retained.
