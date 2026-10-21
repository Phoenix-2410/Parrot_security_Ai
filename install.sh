#!/bin/bash
# =====================================================================
# ParrotSec AI Assistant - Autonomous & Interactive Installation Script
# Tailored for Parrot Security OS, Kali Linux, Debian & Ubuntu
# =====================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🦜 Installing ParrotSec AI Assistant for Parrot Security OS..."

# Verify root/sudo privileges
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Please run installation with sudo: sudo ./install.sh"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo "ℹ️  Detected System: $NAME ($VERSION)"
fi

echo "📦 Installing system packages and dependencies..."
apt-get update -y || true
apt-get install -y python3 python3-pip python3-tk python3-requests git curl nmap nikto sqlmap gobuster hydra hashcat || true

# Handle Python packages (PEP 668 Debian/Parrot compatibility)
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo "🐍 Installing Python requirements..."
    python3 -m pip install --break-system-packages -r requirements.txt 2>/dev/null || \
    python3 -m pip install -r requirements.txt 2>/dev/null || true
fi

# Ensure directories exist
mkdir -p "$SCRIPT_DIR/plugins"
mkdir -p "$SCRIPT_DIR/sessions"
mkdir -p "$HOME/.parrotsec_tools"

# Set executable permissions on all entrypoints
chmod +x "$SCRIPT_DIR/parrot-ai"
chmod +x "$SCRIPT_DIR/parrot_ai.py"
chmod +x "$SCRIPT_DIR/parrot_ai_v5.py"
chmod +x "$SCRIPT_DIR/install.sh"

# Install symlinks to system bin so user can run 'parrot-ai' from anywhere
echo "🔗 Creating global command symlinks (/usr/local/bin/parrot-ai)..."
ln -sf "$SCRIPT_DIR/parrot-ai" /usr/local/bin/parrot-ai
ln -sf "$SCRIPT_DIR/parrot-ai" /usr/local/bin/parrotsec-ai

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🦜 PARROTSEC AI ASSISTANT INSTALLED!                ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  You can now run ParrotSec AI from ANY directory:            ║"
echo "║                                                              ║"
echo "║  Interactive Menu Mode:                                      ║"
echo "║    sudo parrot-ai                                            ║"
echo "║                                                              ║"
echo "║  Autonomous Self-Dev Tool Mode (GitHub auto-clone & run):    ║"
echo "║    sudo parrot-ai autotool \"subdomain enum\" target.com        ║"
echo "║    sudo parrot-ai autotool \"sql injection\" http://target/id=1 ║"
echo "║                                                              ║"
echo "║  Direct Fast Scans:                                          ║"
echo "║    sudo parrot-ai scan 192.168.1.1                           ║"
echo "║    sudo parrot-ai smartrecon 192.168.1.1                     ║"
echo "║    sudo parrot-ai workflow full_recon 192.168.1.1            ║"
echo "║                                                              ║"
echo "║  Help & Manual:                                              ║"
echo "║    parrot-ai --help                                          ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
