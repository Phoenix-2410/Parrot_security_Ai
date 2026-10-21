#!/usr/bin/env python3
"""
ParrotSec AI Assistant v5.0 - ENHANCED INTERACTIVE EDITION
Features: Color output, ASCII art banners, Sound notifications, Macro recording
For authorized security testing and educational purposes only
"""

import os
import sys

# Ensure script directory is first in sys.path (needed for Parrot OS global execution / symlinks)
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import json
import subprocess
import shlex
import re
import time
import threading
import sqlite3
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from html import escape

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Advanced Modules Imports
try:
    from modules.github_tool_engine import (
        AutoToolResolver,
        GitHubToolFinder,
        ToolInstaller,
        ToolRegistry,
        TOOL_CATEGORIES
    )
    from modules.advanced_features import (
        TaskAutomationEngine,
        SmartRecon,
        PluginManager,
        SessionManager,
        NetworkMapper,
        ExploitSuggester
    )
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    print(f"Warning: Advanced modules could not be loaded: {e}")

# GUI imports
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

# API imports
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class Colors:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright foreground colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

    @classmethod
    def disable(cls):
        """Disable colors (for non-terminal output)"""
        for attr in dir(cls):
            if not attr.startswith('_') and isinstance(getattr(cls, attr), str):
                setattr(cls, attr, "")

    @classmethod
    def enabled(cls) -> bool:
        """Check if colors should be enabled"""
        return sys.stdout.isatty() and os.environ.get('NO_COLOR') is None

    @staticmethod
    def c(text: str, color: str) -> str:
        """Colorize text"""
        if Colors.enabled():
            return f"{color}{text}{Colors.RESET}"
        return text

    @staticmethod
    def severity(sev: str) -> str:
        """Color by severity"""
        colors = {
            'critical': Colors.BG_RED + Colors.BOLD + Colors.WHITE,
            'high': Colors.BRIGHT_RED,
            'medium': Colors.BRIGHT_YELLOW,
            'low': Colors.BRIGHT_BLUE,
            'info': Colors.BRIGHT_CYAN
        }
        return Colors.c(sev.upper(), colors.get(sev.lower(), Colors.WHITE))

    @staticmethod
    def success(text: str) -> str:
        return Colors.c(f"✅ {text}", Colors.BRIGHT_GREEN)

    @staticmethod
    def error(text: str) -> str:
        return Colors.c(f"❌ {text}", Colors.BRIGHT_RED)

    @staticmethod
    def warning(text: str) -> str:
        return Colors.c(f"⚠️  {text}", Colors.BRIGHT_YELLOW)

    @staticmethod
    def info(text: str) -> str:
        return Colors.c(f"ℹ️  {text}", Colors.BRIGHT_CYAN)

    @staticmethod
    def header(text: str) -> str:
        return Colors.c(text, Colors.BOLD + Colors.BRIGHT_MAGENTA)


class SoundNotifier:
    """Sound notifications using system bell or beep"""

    ENABLED = True

    @classmethod
    def toggle(cls):
        """Toggle sounds on/off"""
        cls.ENABLED = not cls.ENABLED
        return cls.ENABLED

    @classmethod
    def bell(cls):
        """System bell"""
        if cls.ENABLED:
            print("\a", end="", flush=True)

    @classmethod
    def success(cls):
        """Success sound (happy beep)"""
        if cls.ENABLED:
            print("\a", end="", flush=True)
            time.sleep(0.1)
            print("\a", end="", flush=True)

    @classmethod
    def error(cls):
        """Error sound (double bell)"""
        if cls.ENABLED:
            for _ in range(2):
                print("\a", end="", flush=True)
                time.sleep(0.15)

    @classmethod
    def alert(cls):
        """Alert sound (triple bell)"""
        if cls.ENABLED:
            for _ in range(3):
                print("\a", end="", flush=True)
                time.sleep(0.1)

    @classmethod
    def scan_complete(cls):
        """Scan complete sound"""
        if cls.ENABLED:
            print("\a", end="", flush=True)
            time.sleep(0.2)
            print("\a", end="", flush=True)
            time.sleep(0.2)
            print("\a", end="", flush=True)


class Banner:
    """ASCII art banners"""

    BANNERS = {
        'main': r"""
{c.magenta}{c.bold}
    ____                           ____                    
   / __ \_________  _  ____  __  / ___/_  ______ __      __
  / /_/ / ___/ __ \| |/_/ / / /  \__ \/ / / / __ `/ | /| / /
 / ____/ /  / /_/ />  </ /_/ /  ___/ / /_/ / /_/ /| |/ |/ / 
/_/   /_/   \____/_/|_|\__, /  /____/\__,_/\__,_/ |__/|__/  
                      /____/                                 
{c.reset}
{c.cyan}        ____  __    _      __                
       / __ \/ /_  (_)____/ /_____  ____ ___ 
      / / / / __ \/ / ___/ __/ __ \/ __ `__ \
     / /_/ / /_/ / (__  ) /_/ /_/ / / / / / /
     \____/_.___/_/____/\__/\____/_/ /_/ /_/ {c.reset}""",
        'scan': r"""
{c.blue}{c.bold}
   _____                 ____   ____   ______          __
  / ___/____  ___  ____ / __ \ / __ \ / ____/___  ____/ /
  \__ \/ __ \/ _ \/ __ `/ / / // /_/ // /   / __ \/ __  / 
 ___/ / /_/ /  __/ /_/ / /_/ // _, _/ /___/ /_/ / /_/ /  
/____/\____/\___/\__, /_____(_)_/ |_|\____/\____/\__,_/   
                 /____/                                   {c.reset}""",
        'recon': r"""
{c.green}{c.bold}
    ____                           
   / __ \___  _________  _________
  / /_/ / _ \/ ___/ __ \/ ___/ __ \
 / _, _/  __/ /__/ /_/ / /  / /_/ /
/_/ |_|\___/\___/\____/_/   \____/ 
{c.reset}""",
        'exploit': r"""
{c.red}{c.bold}
    ______           __  _            __ 
   / ____/  _______/ /_(_)___  ___  / /_
  / __/ | |/_/ ___/ __/ / __ \/ _ \/ __/
 / /___>  </ /__/ /_/ / / / /  __/ /_  
/_____/_/|_|\___/\__/_/_/ /_/\___/\__/  {c.reset}""",
        'wireless': r"""
{c.magenta}{c.bold}
 _       ___          __               
| |     / (_)_______ / /__  __________ 
| | /| / / / ___/ _ \/ / _ \/ ___/ ___/ 
| |/ |/ / / /  /  __/ /  __(__  |__  )  
|__/|__/_/_/   \___/_/\___/____/____/   {c.reset}""",
        'report': r"""
{c.yellow}{c.bold}
    ____                              __   
   / __ \____ __________ _____  ____/ /__ 
  / /_/ / __ `/ ___/ __ `/ __ \/ __  / _ \
 / _, _/ /_/ / /  / /_/ / / / / /_/ /  __/
/_/ |_|\__,_/_/   \__,_/_/ /_/\__,_/\___/ {c.reset}"""
    }

    @classmethod
    def show(cls, name: str = 'main'):
        """Show a banner with colors"""
        template = cls.BANNERS.get(name, cls.BANNERS['main'])
        colored = template.format(
            c=type('C', (), {
                'magenta': Colors.BRIGHT_MAGENTA, 'blue': Colors.BRIGHT_BLUE,
                'green': Colors.BRIGHT_GREEN, 'red': Colors.BRIGHT_RED,
                'yellow': Colors.BRIGHT_YELLOW, 'cyan': Colors.BRIGHT_CYAN,
                'bold': Colors.BOLD, 'reset': Colors.RESET
            })
        )
        print(colored)


class MacroRecorder:
    """Record and replay command sequences"""

    def __init__(self, db_path: str = "parrotsec_macros.db"):
        self.db_path = db_path
        self.recording = False
        self.current_macro: List[str] = []
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS macros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                commands TEXT,
                description TEXT,
                created TEXT
            )
        """)
        conn.commit()
        conn.close()

    def start_recording(self, name: str, description: str = ""):
        """Start recording a macro"""
        self.recording = True
        self.current_macro = []
        self.macro_name = name
        self.macro_desc = description
        print(Colors.info(f"Started recording macro '{name}'"))
        print(Colors.dim + "  Type commands. Type 'stop' to finish." + Colors.RESET)

    def record(self, command: str) -> bool:
        """Record a command. Returns False if should stop"""
        if command.strip().lower() == 'stop':
            return False
        self.current_macro.append(command)
        print(Colors.dim + f"  [{len(self.current_macro)}] Recorded" + Colors.RESET)
        return True

    def stop_recording(self):
        """Stop and save macro"""
        self.recording = False

        if not self.current_macro:
            print(Colors.warning("Macro empty, not saved"))
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO macros (name, commands, description, created)
            VALUES (?, ?, ?, ?)
        """, (self.macro_name, json.dumps(self.current_macro), 
              self.macro_desc, datetime.now().isoformat()))
        conn.commit()
        conn.close()

        print(Colors.success(f"Macro '{self.macro_name}' saved ({len(self.current_macro)} commands)"))
        SoundNotifier.success()

    def list_macros(self) -> List[Dict]:
        """List all macros"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM macros")
        macros = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return macros

    def load_macro(self, name: str) -> Optional[List[str]]:
        """Load macro commands"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT commands FROM macros WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return json.loads(result[0])
        return None

    def delete_macro(self, name: str) -> bool:
        """Delete a macro"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM macros WHERE name = ?", (name,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    def execute_macro(self, name: str, ai) -> bool:
        """Execute a macro"""
        commands = self.load_macro(name)
        if not commands:
            print(Colors.error(f"Macro '{name}' not found"))
            return False

        print(Colors.info(f"Executing macro '{name}' ({len(commands)} commands)"))

        for i, cmd in enumerate(commands, 1):
            print(Colors.c(f"  [{i}/{len(commands)}] ", Colors.BRIGHT_BLACK) + cmd)
            result = ai.run_command(cmd)
            if not result.success and not ai.menu.confirm("Command failed. Continue?", default=True):
                break

        SoundNotifier.scan_complete()
        print(Colors.success(f"Macro '{name}' complete"))
        return True


@dataclass
class CommandResult:
    success: bool
    output: str
    error: str
    return_code: int
    command: str
    timestamp: str
    duration: float
    parsed_data: Optional[Dict] = None


@dataclass
class Finding:
    severity: str
    title: str
    description: str
    target: str
    tool: str
    remediation: str
    references: List[str] = field(default_factory=list)


class DatabaseManager:
    """SQLite database"""

    def __init__(self, db_path: str = "parrotsec_ai.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                severity TEXT, title TEXT, description TEXT,
                target TEXT, tool TEXT, remediation TEXT,
                "references" TEXT, timestamp TEXT, scan_id INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT, tool TEXT, command TEXT,
                timestamp TEXT, duration REAL, success BOOLEAN
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT UNIQUE, api_key TEXT, enabled BOOLEAN DEFAULT 1
            )
        """)

        conn.commit()
        conn.close()

    def add_finding(self, finding: Finding, scan_id: int = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO findings (severity, title, description, target, tool, 
                                remediation, "references", timestamp, scan_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (finding.severity, finding.title, finding.description,
              finding.target, finding.tool, finding.remediation,
              json.dumps(finding.references), datetime.now().isoformat(), scan_id))
        fid = cursor.lastrowid
        conn.commit()
        conn.close()
        return fid

    def add_scan(self, target, tool, command, duration, success) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scans (target, tool, command, timestamp, duration, success)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (target, tool, command, datetime.now().isoformat(), duration, success))
        sid = cursor.lastrowid
        conn.commit()
        conn.close()
        return sid

    def get_findings(self, severity=None, target=None, limit=100) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT * FROM findings WHERE 1=1"
        params = []
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if target:
            query += " AND target = ?"
            params.append(target)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        results = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return results

    def get_statistics(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM findings")
        stats['total_findings'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM scans")
        stats['total_scans'] = cursor.fetchone()[0]
        cursor.execute("SELECT severity, COUNT(*) FROM findings GROUP BY severity")
        stats['by_severity'] = dict(cursor.fetchall())
        conn.close()
        return stats

    def save_api_key(self, service: str, api_key: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO api_keys (service, api_key, enabled)
            VALUES (?, ?, 1)
        """, (service, api_key))
        conn.commit()
        conn.close()

    def get_api_key(self, service: str) -> Optional[str]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT api_key FROM api_keys WHERE service = ? AND enabled = 1", (service,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None


class ShodanAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.shodan.io"

    def search(self, query, limit=100):
        if not self.api_key:
            return {'error': 'No API key configured'}
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests not installed'}
        try:
            r = requests.get(f"{self.base_url}/shodan/host/search",
                           params={'key': self.api_key, 'query': query, 'limit': limit})
            return r.json()
        except Exception as e:
            return {'error': str(e)}

    def host_info(self, ip):
        if not self.api_key:
            return {'error': 'No API key configured'}
        try:
            r = requests.get(f"{self.base_url}/shodan/host/{ip}", params={'key': self.api_key})
            return r.json()
        except Exception as e:
            return {'error': str(e)}


class VirusTotalAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/vtapi/v2"

    def scan_url(self, url):
        if not self.api_key:
            return {'error': 'No API key configured'}
        if not REQUESTS_AVAILABLE:
            return {'error': 'requests not installed'}
        try:
            r = requests.post(f"{self.base_url}/url/scan",
                            data={'apikey': self.api_key, 'url': url})
            return r.json()
        except Exception as e:
            return {'error': str(e)}

    def get_ip_report(self, ip):
        if not self.api_key:
            return {'error': 'No API key configured'}
        try:
            r = requests.get(f"{self.base_url}/ip-address/report",
                           params={'apikey': self.api_key, 'ip': ip})
            return r.json()
        except Exception as e:
            return {'error': str(e)}


class OutputParser:
    @staticmethod
    def parse_nmap(output: str) -> Dict:
        hosts = []
        current_host = None
        for line in output.split('\n'):
            m = re.search(r'Nmap scan report for (.+)', line)
            if m:
                if current_host:
                    hosts.append(current_host)
                current_host = {'ip': m.group(1), 'ports': []}
            m = re.search(r'(\d+)/(tcp|udp)\s+(open)\s+(\S+)\s*(.*)', line)
            if m and current_host:
                current_host['ports'].append({
                    'port': int(m.group(1)), 'protocol': m.group(2),
                    'service': m.group(4), 'version': m.group(5).strip() if m.group(5) else ''
                })
        if current_host:
            hosts.append(current_host)
        return {'hosts': hosts, 'total_hosts': len(hosts)}

    @staticmethod
    def parse_nikto(output: str) -> Dict:
        findings = []
        for line in output.split('\n'):
            m = re.search(r'\+ (.+): (.+)', line)
            if m and 'Target' not in m.group(1):
                findings.append({'type': m.group(1), 'detail': m.group(2)})
        return {'findings': findings, 'total_findings': len(findings)}


class InteractiveMenu:
    """Enhanced interactive menu with colors and sounds"""

    @staticmethod
    def get_input(prompt: str, default: str = "", required: bool = False) -> str:
        while True:
            prompt_str = Colors.c(f"{prompt}", Colors.BRIGHT_CYAN)
            if default:
                prompt_str += Colors.c(f" [{default}]", Colors.BRIGHT_BLACK)
            prompt_str += ": "

            try:
                value = input(prompt_str).strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return default

            if not value and default:
                return default
            if not value and required:
                print(Colors.error("This field is required"))
                continue
            return value

    @staticmethod
    def get_choice(options: List[str], prompt: str = "Select option") -> int:
        print(f"\n{Colors.c(prompt + ':', Colors.BRIGHT_YELLOW)}")
        for i, opt in enumerate(options, 1):
            num = Colors.c(f"[{i}]", Colors.BRIGHT_MAGENTA)
            print(f"  {num} {opt}")

        while True:
            try:
                choice = input(Colors.c(f"\nEnter choice (1-{len(options)}): ", Colors.BRIGHT_CYAN)).strip()
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return idx
                print(Colors.error(f"Enter a number between 1 and {len(options)}"))
                SoundNotifier.bell()
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            except ValueError:
                print(Colors.error("Enter a valid number"))
                SoundNotifier.bell()

    @staticmethod
    def confirm(prompt: str, default: bool = True) -> bool:
        suffix = Colors.c("[Y/n]", Colors.BRIGHT_GREEN) if default else Colors.c("[y/N]", Colors.BRIGHT_RED)
        prompt_str = f"{Colors.c(prompt, Colors.BRIGHT_YELLOW)} {suffix}: "

        while True:
            try:
                response = input(prompt_str).strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return default

            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print(Colors.error("Enter 'y' or 'n'"))

    @staticmethod
    def show_progress(message: str, duration: float = 1.0):
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        colored_msg = Colors.c(message, Colors.BRIGHT_BLUE)
        for _ in range(int(duration * 10)):
            for char in chars:
                print(f"\r{Colors.BRIGHT_CYAN}{char}{Colors.RESET} {colored_msg}", end="", flush=True)
                time.sleep(0.1)
        print(f"\r{Colors.success(message + ' Complete!')}                    ")

    @staticmethod
    def show_table(headers: List[str], rows: List[List[str]]):
        if not rows:
            print(Colors.dim + "No data to display" + Colors.RESET)
            return

        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        border_color = Colors.BRIGHT_BLACK
        header_color = Colors.BOLD + Colors.BRIGHT_CYAN

        top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
        bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

        print(Colors.c(top, border_color))
        header_row = "│" + "│".join(f" {Colors.c(h, header_color):<{w + len(Colors.c(h, header_color)) - len(h)}} " for h, w in zip(headers, col_widths)) + "│"
        print(header_row + Colors.RESET)
        print(Colors.c(mid, border_color))

        for row in rows:
            cells = "│" + "│".join(f" {str(c):<{w}} " for c, w in zip(row, col_widths)) + "│"
            print(Colors.c(cells, Colors.WHITE))

        print(Colors.c(bot, border_color))


class ParrotSecAIV5:
    """Main AI Assistant v5.0"""

    def __init__(self):
        self.db = DatabaseManager()
        self.parser = OutputParser()
        self.menu = InteractiveMenu()
        self.macros = MacroRecorder()
        self.current_target = None
        self.history = []
        self.last_scan_result = None

        # Advanced Autonomous & Futuristic Engines
        if MODULES_AVAILABLE:
            self.auto_resolver = AutoToolResolver()
            self.automation = TaskAutomationEngine(self)
            self.smart_recon = SmartRecon(self)
            self.plugins = PluginManager(ai_assistant=self)
            self.session_mgr = SessionManager()
        else:
            self.auto_resolver = None
            self.automation = None
            self.smart_recon = None
            self.plugins = None
            self.session_mgr = None

        shodan_key = self.db.get_api_key('shodan')
        vt_key = self.db.get_api_key('virustotal')
        self.shodan = ShodanAPI(shodan_key)
        self.virustotal = VirusTotalAPI(vt_key)

    def run_interactive(self):
        Banner.show('main')

        if not self.check_authorization():
            sys.exit(1)

        print(Colors.c("\n  🦜 Welcome to ParrotSec AI Assistant v5.0!", Colors.BOLD + Colors.BRIGHT_GREEN))
        print(Colors.c("  Type 'help' for commands or 'menu' for interactive menu\n", Colors.DIM))

        # Command loop with macro support
        while True:
            try:
                prompt = Colors.c("parrot-ai", Colors.BRIGHT_GREEN) + Colors.c("> ", Colors.BRIGHT_BLACK)
                user_input = input(prompt).strip()

                if not user_input:
                    continue

                # Macro recording mode
                if self.macros.recording:
                    if not self.macros.record(user_input):
                        self.macros.stop_recording()
                    self.history.append(user_input)
                    continue

                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                args = cmd_parts[1] if len(cmd_parts) > 1 else ""

                if cmd in ['exit', 'quit']:
                    print(Colors.info("Goodbye!"))
                    SoundNotifier.bell()
                    break
                elif cmd == 'menu':
                    self.main_menu()
                elif cmd == 'help':
                    self.show_help()
                elif cmd == 'run':
                    self.run_command(args)
                elif cmd == 'scan':
                    self.quick_scan(args)
                elif cmd == 'shodan':
                    self.shodan_search(args)
                elif cmd == 'virustotal':
                    self.vt_scan(args)
                elif cmd == 'target':
                    self.current_target = args
                    print(Colors.success(f"Target set: {Colors.BOLD}{args}"))
                elif cmd == 'report':
                    self.generate_report(args)
                elif cmd == 'db':
                    self.show_db_stats()
                elif cmd == 'sounds':
                    enabled = SoundNotifier.toggle()
                    status = "ON 🔔" if enabled else "OFF 🔕"
                    print(Colors.info(f"Sounds: {status}"))
                elif cmd == 'colors':
                    self.toggle_colors()
                elif cmd == 'record':
                    self.start_macro_recording(args)
                elif cmd == 'macros':
                    self.macros_menu()
                elif cmd == 'banner':
                    Banner.show(args if args else 'main')
                elif cmd in ['autotool', 'auto']:
                    self.cmd_autotool(args)
                elif cmd in ['findtool', 'searchtool']:
                    self.cmd_findtool(args)
                elif cmd == 'tools':
                    self.cmd_tools_registry()
                elif cmd in ['smartrecon', 'recon']:
                    self.cmd_smartrecon(args)
                elif cmd in ['workflow', 'playbook']:
                    self.cmd_workflow(args)
                elif cmd == 'workflows':
                    self.cmd_list_workflows()
                elif cmd == 'topology':
                    self.cmd_topology()
                elif cmd == 'exploit':
                    self.exploit_menu()
                elif cmd in ['wireless', 'wifi']:
                    self.wireless_menu()
                elif cmd == 'session':
                    self.cmd_session(args)
                elif cmd == 'plugins':
                    self.cmd_plugins()
                else:
                    print(Colors.error(f"Unknown: {cmd}. Type 'help' or 'menu'"))

                self.history.append(user_input)

            except KeyboardInterrupt:
                print(Colors.warning("\nUse 'exit' to quit"))
            except EOFError:
                print(Colors.info("\nGoodbye!"))
                break
            except Exception as e:
                print(Colors.error(f"Error: {e}"))
                SoundNotifier.error()

    def main_menu(self):
        """Colorful interactive main menu"""
        while True:
            print()
            print(Colors.c("┌─────────────────────────────────────────────────────────────────┐", Colors.BRIGHT_MAGENTA))
            print(Colors.c("│", Colors.BRIGHT_MAGENTA) + Colors.c("  🦜 MAIN MENU", Colors.BOLD + Colors.BRIGHT_WHITE).center(65) + Colors.c("│", Colors.BRIGHT_MAGENTA))
            print(Colors.c("├─────────────────────────────────────────────────────────────────┤", Colors.BRIGHT_MAGENTA))

            menu_items = [
                ("1", "🎯", "Quick Scan", Colors.BRIGHT_GREEN),
                ("2", "🔍", "Reconnaissance", Colors.BRIGHT_BLUE),
                ("3", "🛡️ ", "Vulnerability Scan", Colors.BRIGHT_YELLOW),
                ("4", "🌐", "Web Testing", Colors.BRIGHT_CYAN),
                ("5", "🔐", "Password Testing", Colors.BRIGHT_RED),
                ("6", "📡", "Wireless Testing", Colors.BRIGHT_MAGENTA),
                ("7", "🧬", "Exploitation", Colors.RED),
                ("8", "📊", "Reports", Colors.BRIGHT_YELLOW),
                ("9", "🔌", "API (Shodan/VT)", Colors.BRIGHT_BLUE),
                ("10", "⏺️ ", "Macros", Colors.BRIGHT_GREEN),
                ("11", "⚙️ ", "Settings", Colors.BRIGHT_BLACK),
                ("12", "🤖", "Auto Tool Engine (GitHub)", Colors.BRIGHT_CYAN),
                ("13", "⚡", "Automated Playbooks", Colors.BRIGHT_YELLOW),
                ("14", "🧠", "Smart Adaptive Recon", Colors.BRIGHT_MAGENTA),
                ("15", "🗺️ ", "Topology & Exploits", Colors.BRIGHT_GREEN),
                ("16", "💾", "Session Manager", Colors.CYAN),
                ("17", "🧩", "Plugin Ecosystem", Colors.BLUE),
                ("0", "🚪", "Exit Menu", Colors.BRIGHT_RED),
            ]

            for num, icon, label, color in menu_items:
                line = f"│  {Colors.c('[' + num + ']', color)} {icon} {label}"
                padding = 65 - len(f"  [{num}] {icon} {label}")
                print(line + " " * padding + Colors.c("│", Colors.BRIGHT_MAGENTA))

            print(Colors.c("└─────────────────────────────────────────────────────────────────┘", Colors.BRIGHT_MAGENTA))

            choice = input(Colors.c("\nSelect: ", Colors.BRIGHT_CYAN)).strip()

            if choice == "0":
                break
            elif choice == "1":
                self.quick_scan_interactive()
            elif choice == "2":
                self.recon_menu()
            elif choice == "3":
                self.vuln_menu()
            elif choice == "4":
                self.web_menu()
            elif choice == "5":
                self.password_menu()
            elif choice == "6":
                self.wireless_menu()
            elif choice == "7":
                self.exploit_menu()
            elif choice == "8":
                self.report_menu()
            elif choice == "9":
                self.api_menu()
            elif choice == "10":
                self.macros_menu()
            elif choice == "11":
                self.settings_menu()
            elif choice == "12":
                self.autonomous_tool_interactive()
            elif choice == "13":
                self.automation_menu()
            elif choice == "14":
                self.smart_recon_interactive()
            elif choice == "15":
                self.topology_exploit_interactive()
            elif choice == "16":
                self.session_menu()
            elif choice == "17":
                self.plugin_menu()
            else:
                print(Colors.error(f"Invalid option: '{choice}'. Enter a number from 0 to 17."))

    # -------------------------------------------------------------
    # Futuristic Autonomous & Advanced Engine Handlers
    # -------------------------------------------------------------
    def cmd_autotool(self, args: str):
        """Execute task by autonomously searching GitHub, cloning tool, and running it"""
        if not self.auto_resolver:
            print(Colors.error("AutoTool Engine is not loaded."))
            return

        if not args:
            task = self.menu.get_input("Describe the security task (e.g. 'subdomain discovery', 'sql injection', 'xss', 'jwt')", required=True)
            target = self.current_target or self.menu.get_input("Target host / URL", required=True)
            custom_flags = self.menu.get_input("Optional extra flags (or press Enter)", "")
        else:
            try:
                tokens = shlex.split(args)
            except Exception:
                tokens = args.split()

            flags_list = [t for t in tokens if t.startswith("-")]
            non_flags = [t for t in tokens if not t.startswith("-")]
            custom_flags = " ".join(flags_list)

            if len(non_flags) >= 2:
                target_idx = -1
                for idx, tok in enumerate(non_flags):
                    if tok.startswith(("http://", "https://")) or re.match(r'^\d+\.\d+\.\d+\.\d+', tok) or ("." in tok and not tok.endswith(".")):
                        target_idx = idx
                if target_idx != -1:
                    target = non_flags[target_idx]
                    task_tokens = [t for i, t in enumerate(non_flags) if i != target_idx]
                    task = " ".join(task_tokens)
                else:
                    task = " ".join(non_flags[:-1])
                    target = non_flags[-1]
            elif len(non_flags) == 1:
                task = non_flags[0]
                target = self.current_target or self.menu.get_input("Target host / URL", required=True)
            else:
                task = self.menu.get_input("Describe security task", required=True)
                target = self.current_target or self.menu.get_input("Target host / URL", required=True)

        self.current_target = target
        res = self.auto_resolver.autonomous_resolve_and_execute(
            task_prompt=task,
            target=target,
            custom_args=custom_flags
        )
        if res.get("success"):
            SoundNotifier.scan_complete()
            print(Colors.success(f"Autonomous task '{task}' executed successfully!"))
        else:
            SoundNotifier.error()
            print(Colors.error(f"Autonomous task failed: {res.get('error', 'Unknown issue')}"))

    def cmd_findtool(self, args: str):
        """Search GitHub for security tools"""
        if not self.auto_resolver:
            print(Colors.error("AutoTool Engine is not loaded."))
            return
        query = args or self.menu.get_input("Enter tool capability / keyword to find on GitHub", required=True)
        tools = self.auto_resolver.finder.search_tools(query, limit=5)
        if not tools:
            print(Colors.warning(f"No tools found for '{query}'"))
            return

        headers = ["Tool Name", "Stars", "Language", "Description"]
        rows = []
        for t in tools:
            rows.append([
                Colors.c(t["name"], Colors.BRIGHT_GREEN),
                str(t["stars"]),
                t["language"],
                t["description"][:45] + "..." if len(t["description"]) > 45 else t["description"]
            ])
        self.menu.show_table(headers, rows)

        if self.menu.confirm("Would you like to clone and install one of these tools now?", default=False):
            options = [f"{t['name']} ({t['stars']} ⭐) - {t['html_url']}" for t in tools]
            sel = self.menu.get_choice(options, "Select tool to auto-clone")
            chosen = tools[sel]
            print(Colors.info(f"Cloning {chosen['name']}..."))
            path = self.auto_resolver.installer.clone_repository(chosen["clone_url"], chosen["name"])
            if path:
                strat = self.auto_resolver.installer.detect_install_strategy(path)
                self.auto_resolver.installer.install_dependencies(path, strat)
                self.auto_resolver.registry.register_tool({
                    "name": chosen["name"],
                    "repo_url": chosen["html_url"],
                    "clone_url": chosen["clone_url"],
                    "description": chosen["description"],
                    "stars": chosen["stars"],
                    "language": chosen["language"],
                    "category": chosen.get("category", "general"),
                    "install_path": str(path),
                    "executable_path": strat.get("entrypoint") or str(path),
                    "install_method": strat.get("type", "direct"),
                    "status": "ready"
                })
                print(Colors.success(f"Tool {chosen['name']} is installed and registered in your AI toolchain!"))

    def cmd_tools_registry(self):
        """List all auto-cloned and discovered tools in registry"""
        if not self.auto_resolver:
            print(Colors.error("AutoTool Engine is not loaded."))
            return
        tools = self.auto_resolver.registry.list_all()
        if not tools:
            print(Colors.info("No tools installed in local registry yet. Use 'autotool' or 'findtool' to add tools automatically!"))
            return
        headers = ["Tool", "Category", "Uses", "Status", "Install Path"]
        rows = [
            [
                Colors.c(t["name"], Colors.BRIGHT_GREEN),
                t.get("category", "general"),
                str(t.get("use_count", 0)),
                t.get("status", "ready"),
                t.get("install_path", "")[-30:]
            ]
            for t in tools
        ]
        self.menu.show_table(headers, rows)

    def cmd_smartrecon(self, args: str):
        """Run intelligent adaptive reconnaissance"""
        if not self.smart_recon:
            print(Colors.error("Smart Recon engine not loaded."))
            return
        target = args or self.current_target or self.menu.get_input("Target host / domain", required=True)
        self.current_target = target
        self.smart_recon.run_adaptive_recon(target)

    def cmd_workflow(self, args: str):
        """Execute automated security playbooks"""
        if not self.automation:
            print(Colors.error("Automation engine not loaded."))
            return
        wf_name = args.strip() if args else ""
        if not wf_name:
            workflows = self.automation.list_workflows()
            idx = self.menu.get_choice(workflows, "Select Automated Playbook")
            wf_name = workflows[idx]
        target = self.current_target or self.menu.get_input("Target for workflow", required=True)
        self.current_target = target
        self.automation.run_workflow(wf_name, target)

    def cmd_list_workflows(self):
        """Show available automation playbooks"""
        if not self.automation:
            print(Colors.error("Automation engine not loaded."))
            return
        print(Colors.header("\n📋 Available Automated Playbooks:"))
        for name, steps in self.automation.workflows.items():
            print(Colors.c(f"\n  • {name.upper()}", Colors.BOLD + Colors.BRIGHT_YELLOW))
            for i, s in enumerate(steps, 1):
                print(f"      Step {i}: {s.name} ({s.tool_or_command})")

    def cmd_topology(self):
        """Display ASCII network & service topology map"""
        target = self.current_target or "unknown_host"
        ports_services = []
        if self.last_scan_result and self.last_scan_result.output:
            for line in self.last_scan_result.output.splitlines():
                if "/tcp" in line and "open" in line:
                    parts = line.split()
                    try:
                        p_num = int(parts[0].split("/")[0])
                        svc = parts[2] if len(parts) > 2 else "service"
                        ports_services.append((p_num, svc))
                    except Exception:
                        pass
        if not ports_services:
            ports_services = [(80, "http"), (443, "https"), (22, "ssh")]
        print(Colors.header("\n🗺️ NETWORK & SERVICE TOPOLOGY MAP:"))
        print(NetworkMapper.render_ascii_topology(target, ports_services))

    def cmd_exploit(self):
        """Run exploit suggester against recent scan findings"""
        text_to_scan = ""
        if self.last_scan_result and self.last_scan_result.output:
            text_to_scan = self.last_scan_result.output
        else:
            text_to_scan = "vsftpd 2.3.4 Apache/2.4.49 OpenSSH 7.2p2"

        exploits = ExploitSuggester.analyze_banners(text_to_scan)
        if not exploits:
            print(Colors.info("No immediate high-probability exploit matches found in current banners."))
            return

        print(Colors.header(f"\n💣 EXPLOIT SUGGESTER MATCHES ({len(exploits)} found):"))
        for exp in exploits:
            print(f"  {Colors.severity('critical')} {Colors.c(exp['name'], Colors.BOLD + Colors.BRIGHT_RED)}")
            print(f"     CVE: {exp['cve']} | Metasploit: {exp['msf']}")

    def cmd_session(self, args: str):
        """Session management command"""
        if not self.session_mgr:
            print(Colors.error("Session manager not loaded."))
            return
        parts = args.split(maxsplit=1) if args else []
        action = parts[0].lower() if parts else ""
        name = parts[1] if len(parts) > 1 else "default_session"

        if action == "save":
            self.session_mgr.save_session(name, self)
        elif action == "load":
            self.session_mgr.load_session(name, self)
        else:
            print(Colors.info("Usage: session save <name>  OR  session load <name>"))

    def cmd_plugins(self):
        """List active plugins"""
        if not self.plugins:
            print(Colors.error("Plugin manager not loaded."))
            return
        plugins = self.plugins.list_plugins()
        print(Colors.header(f"\n🧩 ACTIVE PLUGINS ({len(plugins)}):"))
        for p in plugins:
            print(f"  • {Colors.c(p['name'], Colors.BRIGHT_GREEN)} v{p['version']} - {p['description']}")

    # Interactive Menu Handlers
    def autonomous_tool_interactive(self):
        Banner.show('exploit')
        print(Colors.header("\n🤖 AUTONOMOUS GITHUB TOOL ENGINE (SELF-DEV)"))
        options = [
            "Auto-Solve Task (Find Tool on GitHub -> Clone -> Install -> Execute)",
            "Search GitHub for Security Tools & Inspect",
            "View Installed Toolchain Registry",
            "Back"
        ]
        sel = self.menu.get_choice(options, "Autonomous Engine")
        if sel == 0:
            self.cmd_autotool("")
        elif sel == 1:
            self.cmd_findtool("")
        elif sel == 2:
            self.cmd_tools_registry()

    def automation_menu(self):
        Banner.show('scan')
        print(Colors.header("\n⚡ AUTOMATED SECURITY PLAYBOOKS"))
        options = [
            "Run Playbook: Full Automated Reconnaissance",
            "Run Playbook: Web Application Security Audit",
            "Run Playbook: Quick Triage",
            "View Playbook Details",
            "Back"
        ]
        sel = self.menu.get_choice(options, "Select Playbook")
        if sel == 0:
            self.cmd_workflow("full_recon")
        elif sel == 1:
            self.cmd_workflow("web_audit")
        elif sel == 2:
            self.cmd_workflow("quick_triage")
        elif sel == 3:
            self.cmd_list_workflows()

    def smart_recon_interactive(self):
        Banner.show('recon')
        self.cmd_smartrecon("")

    def topology_exploit_interactive(self):
        options = [
            "View ASCII Network Topology Map",
            "Run Exploit Suggester on Recent Scan",
            "Back"
        ]
        sel = self.menu.get_choice(options, "Topology & Exploits")
        if sel == 0:
            self.cmd_topology()
        elif sel == 1:
            self.cmd_exploit()

    def session_menu(self):
        options = ["Save Current Session", "Load Saved Session", "Back"]
        sel = self.menu.get_choice(options, "Session Manager")
        if sel == 0:
            name = self.menu.get_input("Session name", "audit_session_1")
            self.session_mgr.save_session(name, self)
        elif sel == 1:
            name = self.menu.get_input("Session name to load", "audit_session_1")
            self.session_mgr.load_session(name, self)

    def plugin_menu(self):
        self.cmd_plugins()

    def quick_scan_interactive(self):
        """Interactive quick scan"""
        Banner.show('scan')

        if not self.current_target:
            self.current_target = self.menu.get_input("Target IP/hostname", required=True)

        options = [
            "Quick Scan (top 100 ports)",
            "Standard Scan (top 1000 + services)",
            "Full Scan (all ports)"
        ]
        idx = self.menu.get_choice(options, "Scan intensity")

        if not self.menu.confirm(f"Scan {self.current_target}?"):
            return

        self.menu.show_progress("Initializing scan", 1)

        if idx == 0:
            cmd = f"nmap -F {self.current_target}"
        elif idx == 1:
            cmd = f"nmap -sV {self.current_target}"
        else:
            cmd = f"nmap -p- {self.current_target}"

        result = self.run_command(cmd)

        if result.success:
            SoundNotifier.scan_complete()
            self.show_scan_results(result)

            if self.menu.confirm("Run Shodan lookup?"):
                self.shodan_search(f"ip:{self.current_target}")

    def show_scan_results(self, result: CommandResult):
        """Display scan results with colors"""
        if result.parsed_data and result.parsed_data.get('hosts'):
            hosts = result.parsed_data['hosts']

            for host in hosts:
                print(f"\n{Colors.c('Host: ' + host['ip'], Colors.BOLD + Colors.BRIGHT_BLUE)}")

                if host['ports']:
                    headers = ["Port", "Protocol", "Service", "Version"]
                    rows = [[str(p['port']), p['protocol'], 
                             Colors.c(p['service'], Colors.BRIGHT_GREEN),
                             p['version'][:30]] for p in host['ports']]
                    self.menu.show_table(headers, rows)

                    # Color-code risky ports
                    risky = [p for p in host['ports'] if p['port'] in [21, 23, 3389]]
                    if risky:
                        SoundNotifier.alert()
                        for p in risky:
                            sev = 'high' if p['port'] in [23, 3389] else 'medium'
                            print(f"  {Colors.severity(sev)} Open {p['service']} port {p['port']}")

    def recon_menu(self):
        Banner.show('recon')
        if not self.current_target:
            self.current_target = self.menu.get_input("Target", required=True)

        options = ["Port Scan", "OS Detection", "Service Version", "Shodan Search", "Back"]
        idx = self.menu.get_choice(options, "Reconnaissance")

        if idx == 0:
            self.run_command(f"nmap {self.current_target}")
        elif idx == 1:
            self.run_command(f"nmap -O {self.current_target}")
        elif idx == 2:
            self.run_command(f"nmap -sV {self.current_target}")
        elif idx == 3:
            self.shodan_search(self.menu.get_input("Query", required=True))

    def vuln_menu(self):
        if not self.current_target:
            self.current_target = self.menu.get_input("Target", required=True)

        options = ["Nmap Vuln Scripts", "Nikto", "Both", "Back"]
        idx = self.menu.get_choice(options, "Vulnerability Scan")

        if idx in [0, 2]:
            self.run_command(f"nmap --script vuln {self.current_target}")
        if idx in [1, 2]:
            self.run_command(f"nikto -h {self.current_target}")

    def web_menu(self):
        url = self.menu.get_input("URL (http://...)", required=True)
        options = ["Directory Scan", "Nikto", "Both", "Back"]
        idx = self.menu.get_choice(options, "Web Testing")

        if idx in [0, 2]:
            self.run_command(f"gobuster dir -u {url} -w /usr/share/wordlists/dirb/common.txt")
        if idx in [1, 2]:
            self.run_command(f"nikto -h {url}")

    def password_menu(self):
        target = self.menu.get_input("Target", required=True)
        user = self.menu.get_input("Username", "admin")

        options = ["SSH", "FTP", "Back"]
        idx = self.menu.get_choice(options, "Protocol")

        if idx == 0:
            self.run_command(f"hydra -l {user} -P /usr/share/wordlists/rockyou.txt ssh://{target}")
        elif idx == 1:
            self.run_command(f"hydra -l {user} -P /usr/share/wordlists/rockyou.txt ftp://{target}")

    def wireless_menu(self):
        """Wireless security testing menu"""
        Banner.show('wireless')
        options = [
            "Scan WiFi Networks (nmcli / airodump-ng)",
            "Automated WiFi Audit (wifite)",
            "Enable Monitor Mode (airmon-ng start)",
            "Disable Monitor Mode (airmon-ng stop)",
            "Crack WPA/WPA2 Handshake (aircrack-ng)",
            "WPS Network Scan (wash)",
            "Back"
        ]
        idx = self.menu.get_choice(options, "Wireless Testing")

        if idx == 0:
            iface = self.menu.get_input("Wireless interface (leave blank for nmcli scan)", "")
            if iface:
                self.run_command(f"airodump-ng {iface}")
            else:
                self.run_command("nmcli dev wifi list")
        elif idx == 1:
            self.run_command("wifite")
        elif idx == 2:
            iface = self.menu.get_input("Interface to enable monitor mode", "wlan0")
            self.run_command(f"airmon-ng start {iface}")
        elif idx == 3:
            iface = self.menu.get_input("Interface to disable monitor mode", "wlan0mon")
            self.run_command(f"airmon-ng stop {iface}")
        elif idx == 4:
            cap = self.menu.get_input(".cap handshake capture file path", required=True)
            wordlist = self.menu.get_input("Wordlist", "/usr/share/wordlists/rockyou.txt")
            self.run_command(f"aircrack-ng -w {wordlist} {cap}")
        elif idx == 5:
            iface = self.menu.get_input("Monitor mode interface (e.g. wlan0mon)", "wlan0mon")
            self.run_command(f"wash -i {iface}")

    def exploit_menu(self):
        """Exploitation and vulnerability weaponization menu"""
        Banner.show('exploit')
        options = [
            "AI Exploit Suggester (Analyze service banners for CVEs/Metasploit)",
            "Search Exploit-DB (searchsploit)",
            "Launch Metasploit Framework (msfconsole)",
            "Generate Payload (msfvenom)",
            "Back"
        ]
        idx = self.menu.get_choice(options, "Exploitation")

        if idx == 0:
            self.cmd_exploit()
        elif idx == 1:
            query = self.menu.get_input("Exploit search query (service / version / CVE)", required=True)
            self.run_command(f"searchsploit {query}")
        elif idx == 2:
            self.run_command("msfconsole")
        elif idx == 3:
            payload = self.menu.get_input("Payload (e.g. linux/x64/meterpreter/reverse_tcp)", "linux/x64/meterpreter/reverse_tcp")
            lhost = self.menu.get_input("LHOST (your IP)", required=True)
            lport = self.menu.get_input("LPORT", "4444")
            fmt = self.menu.get_input("Format (elf, exe, raw, python)", "elf")
            out = self.menu.get_input("Output filename", f"payload.{fmt}")
            self.run_command(f"msfvenom -p {payload} LHOST={lhost} LPORT={lport} -f {fmt} -o {out}")

    def report_menu(self):
        options = ["Generate HTML Report", "View Statistics", "View Findings", "Export JSON", "Back"]
        idx = self.menu.get_choice(options, "Reports")

        if idx == 0:
            self.generate_report()
        elif idx == 1:
            self.show_db_stats()
        elif idx == 2:
            self.show_findings()
        elif idx == 3:
            self.export_json()

    def api_menu(self):
        options = ["Shodan Search", "Shodan Host Info", "VirusTotal URL", "Set API Keys", "Back"]
        idx = self.menu.get_choice(options, "API")

        if idx == 0:
            self.shodan_search(self.menu.get_input("Query", required=True))
        elif idx == 1:
            r = self.shodan.host_info(self.menu.get_input("IP", required=True))
            print(json.dumps(r, indent=2)[:1500])
        elif idx == 2:
            r = self.virustotal.scan_url(self.menu.get_input("URL", required=True))
            print(json.dumps(r, indent=2)[:1000])
        elif idx == 3:
            svc = self.menu.get_choice(["Shodan", "VirusTotal"], "Service")
            key = self.menu.get_input("API Key", required=True)
            name = 'shodan' if svc == 0 else 'virustotal'
            self.db.save_api_key(name, key)
            if name == 'shodan':
                self.shodan.api_key = key
            else:
                self.virustotal.api_key = key
            print(Colors.success("API key saved"))

    def macros_menu(self):
        """Macro management menu"""
        while True:
            options = ["List Macros", "Record New Macro", "Run Macro", "Delete Macro", "Back"]
            idx = self.menu.get_choice(options, "Macro Manager")

            if idx == 0:
                macros = self.macros.list_macros()
                if macros:
                    headers = ["Name", "Commands", "Created"]
                    rows = [[m['name'], str(len(json.loads(m['commands']))), m['created'][:19]] for m in macros]
                    self.menu.show_table(headers, rows)
                else:
                    print(Colors.info("No macros saved"))

            elif idx == 1:
                name = self.menu.get_input("Macro name", required=True)
                desc = self.menu.get_input("Description", "")
                self.macros.start_recording(name, desc)
                print(Colors.warning("Recording... enter commands, 'stop' to finish"))
                while self.macros.recording:
                    cmd = input(Colors.c("  record> ", Colors.BRIGHT_RED)).strip()
                    if not self.macros.record(cmd):
                        break
                self.macros.stop_recording()

            elif idx == 2:
                macros = self.macros.list_macros()
                if not macros:
                    print(Colors.info("No macros"))
                    continue
                names = [m['name'] for m in macros]
                sel = self.menu.get_choice(names, "Select macro")
                self.macros.execute_macro(names[sel], self)

            elif idx == 3:
                macros = self.macros.list_macros()
                if macros:
                    names = [m['name'] for m in macros]
                    sel = self.menu.get_choice(names, "Delete which?")
                    if self.menu.confirm(f"Delete '{names[sel]}'?", default=False):
                        self.macros.delete_macro(names[sel])
                        print(Colors.success("Deleted"))

            elif idx == 4:
                break

    def start_macro_recording(self, name: str):
        """Quick record from CLI"""
        if not name:
            name = self.menu.get_input("Macro name", required=True)
        self.macros.start_recording(name)

    def settings_menu(self):
        options = ["Toggle Sounds", "Set Target", "View History", "Back"]
        idx = self.menu.get_choice(options, "Settings")

        if idx == 0:
            enabled = SoundNotifier.toggle()
            print(Colors.info(f"Sounds: {'ON 🔔' if enabled else 'OFF 🔕'}"))
        elif idx == 1:
            self.current_target = self.menu.get_input("Target", required=True)
            print(Colors.success(f"Target: {self.current_target}"))
        elif idx == 2:
            print(Colors.c("\nCommand History:", Colors.BOLD))
            for i, h in enumerate(self.history[-15:], 1):
                print(f"  {Colors.c(str(i), Colors.BRIGHT_BLACK)} {h}")

    def toggle_colors(self):
        if Colors.enabled():
            Colors.disable()
            print(Colors.info("Colors disabled"))
        else:
            print(Colors.info("Restart to enable colors"))

    def run_command(self, command: str, timeout: int = 300) -> CommandResult:
        start_time = time.time()

        dangerous = ['rm -rf /', 'mkfs', 'dd if=/dev/zero']
        if any(d in command for d in dangerous):
            print(Colors.error("Dangerous command blocked"))
            SoundNotifier.error()
            return CommandResult(False, "", "Blocked", 1, command, "", 0)

        print(f"\n{Colors.c('$ ' + command, Colors.BRIGHT_GREEN)}")
        print(Colors.c("─" * 60, Colors.BRIGHT_BLACK))

        try:
            process = subprocess.Popen(
                shlex.split(command),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate(timeout=timeout)
            duration = time.time() - start_time

            result = CommandResult(
                process.returncode == 0, stdout, stderr,
                process.returncode, command, datetime.now().isoformat(), duration
            )
            self.last_scan_result = result

            scan_id = self.db.add_scan(
                self.current_target or "unknown",
                command.split()[0], command, duration, result.success
            )

            if result.success:
                if stdout:
                    print(stdout[:2000])
                SoundNotifier.success()
            else:
                if stderr:
                    print(Colors.c(stderr[:500], Colors.RED))

            return result

        except subprocess.TimeoutExpired:
            process.kill()
            print(Colors.error("Command timed out"))
            return CommandResult(False, "", "Timeout", -1, command, "", timeout)
        except Exception as e:
            print(Colors.error(str(e)))
            SoundNotifier.error()
            return CommandResult(False, "", str(e), -1, command, "", 0)

    def quick_scan(self, target: str):
        if not target:
            print(Colors.error("Usage: scan <target>"))
            return
        self.current_target = target
        self.run_command(f"nmap -sV -F {target}")

    def shodan_search(self, query: str):
        if not query:
            print(Colors.error("Usage: shodan <query>"))
            return
        result = self.shodan.search(query)
        if 'error' in result:
            print(Colors.error(result['error']))
        else:
            print(Colors.success(f"Found {result.get('total', 0)} results"))
            for m in result.get('matches', [])[:5]:
                print(f"  {Colors.c(m.get('ip_str'), Colors.BRIGHT_GREEN)}:{m.get('port')} - {m.get('org', 'N/A')[:30]}")

    def vt_scan(self, url: str):
        if not url:
            print(Colors.error("Usage: virustotal <url>"))
            return
        result = self.virustotal.scan_url(url)
        if 'error' in result:
            print(Colors.error(result['error']))
        else:
            print(Colors.success(f"Scan ID: {result.get('scan_id', 'N/A')}"))

    def generate_report(self, filename: str = ""):
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        findings = self.db.get_findings(limit=500)
        stats = self.db.get_statistics()

        html = f"""<!DOCTYPE html><html><head><title>Security Report</title>
<style>body{{font-family:Arial;margin:40px;background:#f5f5f5}}
.header{{background:#2c3e50;color:white;padding:30px;border-radius:10px}}
.section{{background:white;padding:20px;margin:20px 0;border-radius:5px}}
.finding{{border-left:4px solid #e74c3c;padding:10px;margin:10px 0}}
.critical{{border-color:#c0392b}}.high{{border-color:#e74c3c}}
.medium{{border-color:#f39c12}}.low{{border-color:#3498db}}</style></head><body>
<div class="header"><h1>Security Assessment Report</h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p></div>
<div class="section"><h2>Summary</h2>
<p>Findings: {stats['total_findings']} | Scans: {stats['total_scans']}</p></div>
<div class="section"><h2>Findings</h2>"""

        for f in findings:
            html += f"""<div class="finding {f['severity']}">
<b>[{f['severity'].upper()}]</b> {escape(f['title'])}<br>
Target: {escape(f['target'])} | Tool: {escape(f['tool'])}</div>"""

        html += "</div></body></html>"

        with open(filename, 'w') as fh:
            fh.write(html)
        print(Colors.success(f"Report: {filename}"))

    def show_db_stats(self):
        stats = self.db.get_statistics()
        headers = ["Metric", "Value"]
        rows = [
            ["Total Findings", str(stats['total_findings'])],
            ["Total Scans", str(stats['total_scans'])],
            ["Critical", Colors.c(str(stats['by_severity'].get('critical', 0)), Colors.BRIGHT_RED)],
            ["High", Colors.c(str(stats['by_severity'].get('high', 0)), Colors.RED)],
            ["Medium", Colors.c(str(stats['by_severity'].get('medium', 0)), Colors.YELLOW)],
        ]
        self.menu.show_table(headers, rows)

    def show_findings(self):
        findings = self.db.get_findings(limit=15)
        if findings:
            headers = ["Severity", "Title", "Target"]
            rows = [[Colors.severity(f['severity']), f['title'][:35], f['target']] for f in findings]
            self.menu.show_table(headers, rows)
        else:
            print(Colors.info("No findings"))

    def export_json(self):
        findings = self.db.get_findings(limit=1000)
        fn = f"findings_{datetime.now().strftime('%Y%m%d')}.json"
        with open(fn, 'w') as f:
            json.dump(findings, f, indent=2)
        print(Colors.success(f"Exported to {fn}"))

    def show_help(self):
        help_text = f"""
{Colors.c("CORE COMMANDS:", Colors.BOLD + Colors.BRIGHT_YELLOW)}
  {Colors.c("menu", Colors.BRIGHT_GREEN)}              Interactive menu mode
  {Colors.c("run <cmd>", Colors.BRIGHT_GREEN)}         Execute command directly
  {Colors.c("scan <target>", Colors.BRIGHT_GREEN)}     Quick nmap scan
  {Colors.c("target <host>", Colors.BRIGHT_GREEN)}     Set active target
  {Colors.c("shodan <query>", Colors.BRIGHT_GREEN)}    Shodan search
  {Colors.c("virustotal <url>", Colors.BRIGHT_GREEN)}  VT scan
  {Colors.c("report [file]", Colors.BRIGHT_GREEN)}     Generate HTML report
  {Colors.c("db", Colors.BRIGHT_GREEN)}                Database stats

{Colors.c("🤖 AUTONOMOUS SELF-DEVELOPING GITHUB ENGINE:", Colors.BOLD + Colors.BRIGHT_CYAN)}
  {Colors.c("autotool <task> [target]", Colors.BRIGHT_CYAN)} Auto-find tool on GitHub, clone, install, & run!
  {Colors.c("findtool <query>", Colors.BRIGHT_CYAN)}         Search GitHub security repositories & auto-clone
  {Colors.c("tools", Colors.BRIGHT_CYAN)}                    List all installed & discovered tools in registry

{Colors.c("⚡ AUTOMATION & INTELLIGENCE:", Colors.BOLD + Colors.BRIGHT_MAGENTA)}
  {Colors.c("smartrecon [target]", Colors.BRIGHT_MAGENTA)}      Adaptive multi-stage intelligence gathering
  {Colors.c("workflow <name> [target]", Colors.BRIGHT_MAGENTA)} Run multi-stage automated security playbooks
  {Colors.c("workflows", Colors.BRIGHT_MAGENTA)}                List all available automation playbooks
  {Colors.c("topology", Colors.BRIGHT_MAGENTA)}                 Render ASCII network and service topology map
  {Colors.c("exploit", Colors.BRIGHT_MAGENTA)}                  Exploitation & Metasploit weaponization menu
  {Colors.c("wireless", Colors.BRIGHT_MAGENTA)}                 Wireless & WiFi security testing menu
  {Colors.c("session save/load <name>", Colors.BRIGHT_MAGENTA)} Save/resume state and findings
  {Colors.c("plugins", Colors.BRIGHT_MAGENTA)}                  Show dynamic plugins

{Colors.c("UTILITIES:", Colors.BOLD + Colors.BRIGHT_BLUE)}
  {Colors.c("record <name>", Colors.BRIGHT_BLUE)}       Start macro recording
  {Colors.c("macros", Colors.BRIGHT_BLUE)}              Macro manager
  {Colors.c("sounds", Colors.BRIGHT_BLUE)}              Toggle sounds
  {Colors.c("colors", Colors.BRIGHT_BLUE)}              Toggle colors
  {Colors.c("banner [name]", Colors.BRIGHT_BLUE)}       Show ASCII banner
        """
        print(help_text)

    def check_authorization(self, auto_confirm: bool = False) -> bool:
        if auto_confirm or os.environ.get("PARROT_AI_AUTHORIZED") == "1":
            return True

        print()
        print(Colors.c("═" * 60, Colors.BRIGHT_YELLOW))
        print(Colors.c("⚠️  AUTHORIZATION REQUIRED", Colors.BOLD + Colors.BRIGHT_YELLOW))
        print(Colors.c("═" * 60, Colors.BRIGHT_YELLOW))
        print("This tool is for AUTHORIZED security testing only.")
        print("Unauthorized access is illegal.")

        try:
            response = input(Colors.c("\nDo you have authorization? (yes/no): ", Colors.BRIGHT_CYAN)).lower().strip()
            if response in ['yes', 'y', 'true', '1']:
                print(Colors.success("Authorization confirmed"))
                return True
        except (KeyboardInterrupt, EOFError):
            print()

        print(Colors.error("Access denied"))
        SoundNotifier.error()
        return False


def main():
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        print(Colors.warning("Some tools require root on Parrot OS - consider: sudo parrot-ai"))

    ai = ParrotSecAIV5()

    args = sys.argv[1:]
    auto_yes = False
    if "-y" in args:
        auto_yes = True
        args.remove("-y")
    if "--yes" in args:
        auto_yes = True
        args.remove("--yes")

    if not args:
        ai.run_interactive()
        return

    cmd = args[0].lower()
    subargs = " ".join(args[1:]) if len(args) > 1 else ""

    if cmd in ['-h', '--help', 'help']:
        ai.show_help()
        sys.exit(0)
    elif cmd in ['menu', 'interactive']:
        ai.run_interactive()
        return

    if not ai.check_authorization(auto_confirm=auto_yes):
        sys.exit(1)

    # Direct CLI command execution on Parrot OS
    if cmd in ['autotool', 'auto']:
        ai.cmd_autotool(subargs)
    elif cmd in ['findtool', 'searchtool']:
        ai.cmd_findtool(subargs)
    elif cmd == 'tools':
        ai.cmd_tools_registry()
    elif cmd in ['smartrecon', 'recon']:
        ai.cmd_smartrecon(subargs)
    elif cmd in ['workflow', 'playbook']:
        ai.cmd_workflow(subargs)
    elif cmd == 'workflows':
        ai.cmd_list_workflows()
    elif cmd == 'topology':
        ai.cmd_topology()
    elif cmd == 'exploit':
        ai.exploit_menu()
    elif cmd in ['wireless', 'wifi']:
        ai.wireless_menu()
    elif cmd == 'session':
        ai.cmd_session(subargs)
    elif cmd == 'plugins':
        ai.cmd_plugins()
    elif cmd == 'scan':
        ai.quick_scan(subargs)
    elif cmd == 'run':
        ai.run_command(subargs)
    elif cmd == 'shodan':
        ai.shodan_search(subargs)
    elif cmd == 'virustotal':
        ai.vt_scan(subargs)
    elif cmd == 'report':
        ai.generate_report(subargs)
    elif cmd == 'db':
        ai.show_db_stats()
    else:
        print(Colors.error(f"Unknown command: '{cmd}'. Use --help for usage."))
        sys.exit(1)


if __name__ == "__main__":
    main()
