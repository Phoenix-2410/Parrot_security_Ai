# ParrotSec AI Assistant v4.0 - INTERACTIVE EDITION

Advanced AI-powered security tool manager with **interactive wizards**, **guided workflows**, and **step-by-step scanning**.

## 🌟 NEW: Interactive Features

| Feature | Description |
|---------|-------------|
| 🎯 **Quick Start Wizard** | Guided setup for beginners |
| 📋 **Interactive Menus** | Beautiful menu-driven interface |
| 🔄 **Step-by-Step Workflows** | Guided scanning processes |
| 📊 **Real-time Feedback** | Progress indicators and status updates |
| 🎨 **Beautiful Tables** | Formatted output with box-drawing |
| 💡 **Contextual Help** | Built-in tutorials and guides |
| ✅ **Confirmation Prompts** | Safe operation with confirmations |

## 🚀 Quick Start

```bash
# Extract
unzip parrotsec_ai_assistant.zip
cd parrotsec_ai_assistant

# Install
chmod +x install.sh
sudo ./install.sh

# Run INTERACTIVE mode
sudo python3 parrot_ai_v4_interactive.py
```

## 📋 Interactive Menus

### Main Menu Options

| Option | Description |
|--------|-------------|
| [1] Quick Start Wizard | Beginner-friendly guided scan |
| [2] Reconnaissance | Network discovery & enumeration |
| [3] Vulnerability Scan | Find security vulnerabilities |
| [4] Web Application Testing | Test web apps |
| [5] Password & Brute Force | Password testing |
| [6] Wireless Testing | WiFi security testing |
| [7] Exploitation | Metasploit & exploits |
| [8] Reporting | Generate reports |
| [9] API Integrations | Shodan & VirusTotal |
| [10] Plugin Manager | Manage plugins |
| [11] Database & History | View past scans |
| [12] GUI Mode | Graphical interface |
| [13] Settings | Configure options |
| [14] Help & Tutorials | Built-in guides |

## 🎯 Example Interactive Session

```
╔══════════════════════════════════════════════════════════════════════╗
║           🦜 ParrotSec AI Assistant v4.0 - INTERACTIVE               ║
╚══════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────┐
│  📋 MAIN MENU                                                       │
├─────────────────────────────────────────────────────────────────────┤
│  [1] 🎯 Quick Start Wizard        [2] 🔍 Reconnaissance           │
│  [3] 🛡️  Vulnerability Scan       [4] 🌐 Web Application Testing  │
│  ...                                                                │
└─────────────────────────────────────────────────────────────────────┘

Enter your choice: 1

ℹ️  Quick Start Wizard

Enter target: 192.168.1.100

Select scan intensity:
  [1] Quick Scan (5 min)
  [2] Standard Scan (15 min)
  [3] Comprehensive Scan (30+ min)

Enter choice (1-3): 2

Start Standard Scan (15 min) on 192.168.1.100? [Y/n]: y

⠋ Scanning 192.168.1.100...
✅ Scanning 192.168.1.100...

🔧 Executing: nmap -sV -O -A 192.168.1.100
...
```

## 🎨 Beautiful Output

### Tables
```
┌──────────┬────────────────────────────────────────┬─────────────────┬───────┐
│ Severity │ Title                                  │ Target          │ Tool  │
├──────────┼────────────────────────────────────────┼─────────────────┼───────┤
│ HIGH     │ Open ssh port 22                       │ 192.168.1.100   │ nmap  │
│ MEDIUM   │ Open http port 80                      │ 192.168.1.100   │ nmap  │
└──────────┴────────────────────────────────────────┴─────────────────┴───────┘
```

### Progress Indicators
```
⠋ Scanning target...
⠙ Scanning target...
⠹ Scanning target...
✅ Scanning target... Complete!
```

## 📚 Built-in Tutorials

- Getting Started Guide
- Reconnaissance Guide
- Vulnerability Scanning Guide
- Web Testing Guide
- Password Testing Guide

## ⚙️ Requirements

- Parrot OS or Kali Linux
- Python 3.7+
- Root privileges (for some tools)
- Security tools (nmap, nikto, sqlmap, etc.)

## ⚠️ Disclaimer

For authorized security testing only. Unauthorized access is illegal.
