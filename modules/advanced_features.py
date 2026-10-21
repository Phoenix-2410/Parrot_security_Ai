#!/usr/bin/env python3
"""
ParrotSec AI Assistant - Advanced Features Module
Includes:
- TaskAutomationEngine: multi-stage attack & audit pipelines
- SmartRecon: adaptive intelligence gathering
- PluginManager: dynamic plugin ecosystem
- SessionManager: state preservation & project management
- NetworkMapper: visual topology generation
- ExploitSuggester: CVE and attack surface mapping
"""

import os
import sys

# Ensure parent directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import json
import re
import time
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


class Colors:
    """Terminal styling"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    @classmethod
    def enabled(cls) -> bool:
        return sys.stdout.isatty() and os.environ.get('NO_COLOR') is None

    @classmethod
    def c(cls, text: str, color: str) -> str:
        return f"{color}{text}{cls.RESET}" if cls.enabled() else text

    @classmethod
    def success(cls, text: str) -> str:
        return cls.c(f"✅ {text}", cls.BRIGHT_GREEN)

    @classmethod
    def error(cls, text: str) -> str:
        return cls.c(f"❌ {text}", cls.BRIGHT_RED)

    @classmethod
    def warning(cls, text: str) -> str:
        return cls.c(f"⚠️  {text}", cls.BRIGHT_YELLOW)

    @classmethod
    def info(cls, text: str) -> str:
        return cls.c(f"ℹ️  {text}", cls.BRIGHT_CYAN)

    @classmethod
    def header(cls, text: str) -> str:
        return cls.c(text, cls.BOLD + cls.BRIGHT_MAGENTA)


@dataclass
class WorkflowStep:
    name: str
    tool_or_command: str
    args_template: str
    condition: Optional[str] = None
    parse_findings: bool = True
    on_failure: str = "continue"


class TaskAutomationEngine:
    """Executes predefined or dynamic multi-stage automation playbooks"""

    def __init__(self, ai_assistant=None):
        self.ai = ai_assistant
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self._load_builtins()

    def _load_builtins(self):
        # 1. Full Automated Recon Workflow
        self.workflows["full_recon"] = [
            WorkflowStep("Port Discovery", "nmap", "-sV -sC -F {target}"),
            WorkflowStep("Subdomain Enumeration", "auto:subdomain", "{target}"),
            WorkflowStep("Web Path Discovery", "auto:web_fuzzing", "http://{target}"),
            WorkflowStep("OSINT Harvest", "auto:osint", "{target}")
        ]

        # 2. Web Application Assessment
        self.workflows["web_audit"] = [
            WorkflowStep("HTTP Header & Server Analysis", "nikto", "-h {target}"),
            WorkflowStep("Directory Bruteforce", "auto:web_fuzzing", "{target}"),
            WorkflowStep("XSS Vulnerability Scan", "auto:xss", "{target}"),
            WorkflowStep("SQL Injection Probe", "auto:sqli", "{target}")
        ]

        # 3. Quick Triage
        self.workflows["quick_triage"] = [
            WorkflowStep("Top Ports Ping", "nmap", "-F -T4 {target}"),
            WorkflowStep("Service Banner Grab", "nmap", "-sV --version-light {target}")
        ]

    def list_workflows(self) -> List[str]:
        return list(self.workflows.keys())

    def run_workflow(self, workflow_name: str, target: str) -> Dict[str, Any]:
        """Runs an end-to-end multi-step security workflow"""
        if workflow_name not in self.workflows:
            print(Colors.error(f"Workflow '{workflow_name}' not recognized."))
            return {"success": False, "error": "Workflow not found"}

        steps = self.workflows[workflow_name]
        print(Colors.header(f"\n⚡ INITIATING PLAYBOOK: '{workflow_name.upper()}' on {target}"))
        print(Colors.c(f"Total steps: {len(steps)}", Colors.DIM))

        results = []
        for idx, step in enumerate(steps, 1):
            print(Colors.c(f"\n[Step {idx}/{len(steps)}] 🎯 {step.name}", Colors.BOLD + Colors.BRIGHT_CYAN))
            rendered_args = step.args_template.replace("{target}", target)

            if step.tool_or_command.startswith("auto:"):
                # Autonomous GitHub Tool Dispatch
                task_keyword = step.tool_or_command.replace("auto:", "")
                if hasattr(self.ai, "auto_resolver") and self.ai.auto_resolver:
                    step_res = self.ai.auto_resolver.autonomous_resolve_and_execute(
                        task_prompt=task_keyword,
                        target=rendered_args
                    )
                    results.append({"step": step.name, "result": step_res})
                else:
                    print(Colors.warning(f"Auto resolver not linked for task {task_keyword}"))
            else:
                # Direct CLI tool execution
                cmd = f"{step.tool_or_command} {rendered_args}"
                if hasattr(self.ai, "run_command"):
                    step_res = self.ai.run_command(cmd)
                    results.append({"step": step.name, "result": step_res})
                else:
                    print(Colors.info(f"Dry-run command: {cmd}"))

        print(Colors.success(f"\nPlaybook '{workflow_name}' completed across {len(steps)} phases."))
        return {"success": True, "stages": results}


class SmartRecon:
    """Adaptive reconnaissance that automatically triggers specialized follow-up actions"""

    def __init__(self, ai_assistant):
        self.ai = ai_assistant

    def run_adaptive_recon(self, target: str):
        print(Colors.header(f"\n🧠 SMART ADAPTIVE RECONNAISSANCE: {target}"))
        print(Colors.info("Phase 1: Initial Discovery Scan..."))

        # Run fast service detection
        res = self.ai.run_command(f"nmap -F -sV {target}")

        open_ports = []
        services = []

        if res.output:
            for line in res.output.splitlines():
                if "/tcp" in line and "open" in line:
                    parts = line.split()
                    port = parts[0].split("/")[0]
                    svc = parts[2] if len(parts) > 2 else "unknown"
                    open_ports.append(port)
                    services.append(svc)

        print(Colors.c(f"\nDiscovered {len(open_ports)} active ports: {', '.join(open_ports)}", Colors.BRIGHT_GREEN))

        # Dynamically trigger follow-ups based on ports
        follow_ups = []
        if any(p in open_ports for p in ["80", "443", "8080", "8443"]):
            follow_ups.append(("Web Surface", "auto:web_fuzzing", f"http://{target}"))
            follow_ups.append(("Nikto Web Check", "nikto", f"-h http://{target}"))

        if "22" in open_ports:
            follow_ups.append(("SSH Banner Inspection", "nmap", f"-p 22 --script ssh-auth-methods,ssh2-enum-algos {target}"))

        if "21" in open_ports:
            follow_ups.append(("FTP Anon Check", "nmap", f"-p 21 --script ftp-anon {target}"))

        if "445" in open_ports or "139" in open_ports:
            follow_ups.append(("SMB Audit", "nmap", f"-p 445 --script smb-os-discovery,smb-vuln* {target}"))

        print(Colors.c(f"\nIdentified {len(follow_ups)} intelligent follow-up actions:", Colors.BRIGHT_YELLOW))
        for name, tool, args in follow_ups:
            print(f"  • {name} -> {tool} {args}")

        for name, tool, args in follow_ups:
            print(Colors.c(f"\nExecuting intelligent follow-up: {name}...", Colors.BRIGHT_CYAN))
            if tool.startswith("auto:") and hasattr(self.ai, "auto_resolver"):
                task = tool.replace("auto:", "")
                self.ai.auto_resolver.autonomous_resolve_and_execute(task, args)
            else:
                self.ai.run_command(f"{tool} {args}")


class PluginManager:
    """Discovers and hot-loads external Python plugins from plugins/ directory"""

    def __init__(self, plugins_dir: str = "plugins", ai_assistant=None):
        self.plugins_dir = Path(plugins_dir)
        self.ai = ai_assistant
        self.loaded_plugins: Dict[str, Any] = {}
        self.discover_plugins()

    def discover_plugins(self):
        if not self.plugins_dir.exists():
            self.plugins_dir.mkdir(parents=True, exist_ok=True)
            return

        for py_file in self.plugins_dir.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            self.load_plugin(py_file)

    def load_plugin(self, file_path: Path):
        plugin_name = file_path.stem
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, str(file_path))
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

                plugin_cls = getattr(mod, "PluginClass", None)
                if plugin_cls:
                    instance = plugin_cls()
                    self.loaded_plugins[instance.name] = instance
        except Exception as e:
            print(Colors.error(f"Failed to load plugin {file_path.name}: {e}"))

    def list_plugins(self) -> List[Dict]:
        return [
            {
                "name": p.name,
                "version": getattr(p, "version", "1.0.0"),
                "description": getattr(p, "description", "")
            }
            for p in self.loaded_plugins.values()
        ]


class SessionManager:
    """Persists assessment context, findings, target history, and macro states"""

    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_name: str, ai_instance) -> str:
        filepath = self.sessions_dir / f"{session_name}.json"
        data = {
            "name": session_name,
            "target": getattr(ai_instance, "current_target", None),
            "history": getattr(ai_instance, "history", []),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(Colors.success(f"Session saved to {filepath}"))
        return str(filepath)

    def load_session(self, session_name: str, ai_instance) -> bool:
        filepath = self.sessions_dir / f"{session_name}.json"
        if not filepath.exists():
            print(Colors.error(f"Session file {filepath} not found."))
            return False

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        ai_instance.current_target = data.get("target")
        ai_instance.history = data.get("history", [])
        print(Colors.success(f"Session '{session_name}' restored. Target set to: {ai_instance.current_target}"))
        return True


class NetworkMapper:
    """Generates ASCII visual topology maps from discovered hosts & services"""

    @staticmethod
    def render_ascii_topology(target: str, ports_services: List[tuple[int, str]]) -> str:
        lines = [
            r"          [ ParrotSec AI Orchestrator ]",
            r"                        │",
            r"                        ▼",
            f"             [ Target: {target} ]",
            r"             ┌──────────┴──────────┐"
        ]

        if not ports_services:
            lines.append("             │ (No active ports)   │")
            lines.append("             └─────────────────────┘")
            return "\n".join(lines)

        for port, service in ports_services:
            lines.append(f"             ├── Port {port:5d} ──► [{service}]")

        lines.append("             └─────────────────────┘")
        return "\n".join(lines)


class ExploitSuggester:
    """Analyzes open services, banners, and versions to suggest high-impact exploits"""

    DATABASE = [
        {"pattern": r"vsftpd 2\.3\.4", "name": "vsftpd 2.3.4 Backdoor", "cve": "CVE-2011-2523", "msf": "exploit/unix/ftp/vsftpd_234_backdoor"},
        {"pattern": r"Apache.*2\.4\.49", "name": "Apache Path Traversal", "cve": "CVE-2021-41773", "msf": "exploit/multi/http/apache_normalize_path"},
        {"pattern": r"OpenSSH.*(7\.[0-7]|6\.)", "name": "OpenSSH User Enumeration", "cve": "CVE-2018-15473", "msf": "auxiliary/scanner/ssh/ssh_enumusers"},
        {"pattern": r"SMBv1|Windows.*(XP|2003)", "name": "EternalBlue SMB Remote Code Exec", "cve": "CVE-2017-0144", "msf": "exploit/windows/smb/ms17_010_eternalblue"},
        {"pattern": r"ProFTPD 1\.3\.5", "name": "ProFTPD mod_copy Command Exec", "cve": "CVE-2015-3306", "msf": "exploit/unix/ftp/proftpd_modcopy_exec"},
        {"pattern": r"Samba.*(3\.|4\.[0-5])", "name": "SambaCry Remote Code Exec", "cve": "CVE-2017-7494", "msf": "exploit/linux/samba/is_known_pipename"}
    ]

    @classmethod
    def analyze_banners(cls, text: str) -> List[Dict[str, str]]:
        matched = []
        for item in cls.DATABASE:
            if re.search(item["pattern"], text, re.IGNORECASE):
                matched.append(item)
        return matched
