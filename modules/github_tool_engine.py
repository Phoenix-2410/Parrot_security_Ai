#!/usr/bin/env python3
"""
ParrotSec AI Assistant - Autonomous GitHub Tool Engine
Enables self-developing capabilities: automatically finds security tools on GitHub,
clones them, sets up virtual environments / builds dependencies, identifies execution
entrypoints, and runs them autonomously to fulfill security tasks.
"""

import os
import sys

# Ensure parent directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import json
import shutil
import sqlite3
import subprocess
import shlex
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class Colors:
    """ANSI color codes for terminal feedback"""
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


TOOL_CATEGORIES = {
    "port_scanning": {
        "keywords": ["port scan", "port scanner", "network scan", "syn scan", "tcp scan"],
        "github_queries": ["topic:port-scanner language:python", "port scanner stars:>50", "rustscan", "naabu"],
        "known_tools": ["nmap", "rustscan", "masscan", "naabu"],
        "default_tool": "nmap"
    },
    "subdomain_enumeration": {
        "keywords": ["subdomain", "subdomain enum", "dns brute", "dns enum", "passive recon"],
        "github_queries": ["topic:subdomain-enumeration", "subdomain finder language:python", "sublist3r", "amass"],
        "known_tools": ["sublist3r", "subfinder", "amass", "findomain"],
        "default_tool": "subfinder"
    },
    "web_fuzzing": {
        "keywords": ["dir search", "directory brute", "content discovery", "fuzzing", "path discovery"],
        "github_queries": ["topic:directory-bruteforce", "web fuzzer language:python", "ffuf", "dirsearch"],
        "known_tools": ["dirsearch", "ffuf", "gobuster", "feroxbuster"],
        "default_tool": "dirsearch"
    },
    "sql_injection": {
        "keywords": ["sql injection", "sqli", "database exploitation", "sql test"],
        "github_queries": ["topic:sql-injection", "sqli scanner language:python", "sqlmap"],
        "known_tools": ["sqlmap", "ghauri", "dsss"],
        "default_tool": "sqlmap"
    },
    "xss_scanning": {
        "keywords": ["xss", "cross site scripting", "dom xss", "reflected xss"],
        "github_queries": ["topic:xss", "xss scanner language:python", "dalfox", "xsstrike"],
        "known_tools": ["xsstrike", "dalfox", "kxss"],
        "default_tool": "xsstrike"
    },
    "vulnerability_scanning": {
        "keywords": ["cve scan", "vuln scan", "cve lookup", "exploit scan", "vulnerability audit"],
        "github_queries": ["topic:vulnerability-scanner", "cve scanner language:python", "nuclei", "nikto"],
        "known_tools": ["nuclei", "nikto", "flan"],
        "default_tool": "nuclei"
    },
    "cors_misconfig": {
        "keywords": ["cors", "cors misconfiguration", "cross origin"],
        "github_queries": ["topic:cors", "cors scanner language:python", "CORScanner"],
        "known_tools": ["CORScanner", "corsy"],
        "default_tool": "corsy"
    },
    "ssrf_testing": {
        "keywords": ["ssrf", "server side request forgery"],
        "github_queries": ["topic:ssrf", "ssrf scanner", "SSRFmap"],
        "known_tools": ["SSRFmap", "gopherus"],
        "default_tool": "SSRFmap"
    },
    "password_attacks": {
        "keywords": ["brute force", "password spray", "credential audit", "hash cracking"],
        "github_queries": ["topic:bruteforce", "password brute language:python", "hydra"],
        "known_tools": ["hydra", "medusa", "patator"],
        "default_tool": "hydra"
    },
    "jwt_attacks": {
        "keywords": ["jwt", "json web token", "jwt cracker", "jwt tamper"],
        "github_queries": ["topic:jwt", "jwt tool language:python", "jwt_tool"],
        "known_tools": ["jwt_tool", "jwt-cracker"],
        "default_tool": "jwt_tool"
    },
    "cms_scanning": {
        "keywords": ["wordpress", "drupal", "joomla", "cms audit"],
        "github_queries": ["topic:wordpress-scanner", "wpscan", "cmsmap"],
        "known_tools": ["wpscan", "cmsmap", "droopescan"],
        "default_tool": "cmsmap"
    },
    "git_exposure": {
        "keywords": ["git leak", "git dump", "exposed .git", "git extractor"],
        "github_queries": ["topic:git-dumper", "git exposed dump", "GitHack", "GitTools"],
        "known_tools": ["GitHack", "GitTools", "githound"],
        "default_tool": "GitHack"
    },
    "osint_recon": {
        "keywords": ["osint", "whois", "email harvester", "social recon", "domain info"],
        "github_queries": ["topic:osint", "osint tool language:python", "theHarvester", "spiderfoot"],
        "known_tools": ["theHarvester", "sherlock", "spiderfoot", "photon"],
        "default_tool": "theHarvester"
    },
    "api_security": {
        "keywords": ["api scan", "rest api test", "graphql scan", "swagger test"],
        "github_queries": ["topic:api-security", "graphql fuzzer", "kiterunner"],
        "known_tools": ["kiterunner", "clairvoyance", "inql"],
        "default_tool": "kiterunner"
    },
    "reverse_shell_gen": {
        "keywords": ["reverse shell", "payload generator", "shell generation"],
        "github_queries": ["topic:reverse-shell", "payload generator language:python"],
        "known_tools": ["revshell", "msfvenom"],
        "default_tool": "revshell"
    }
}


class GitHubToolFinder:
    """Searches GitHub API for high quality security repositories matching tasks"""

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.api_base = "https://api.github.com"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ParrotSec-AI-AutoDiscovery/5.5"
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"
        return headers

    def _build_search_query(self, task: str) -> Tuple[str, str]:
        """Maps freeform task descriptions into optimal GitHub search queries & identified category"""
        lower_task = task.lower().strip()
        matched_category = "general_security"

        for cat_name, info in TOOL_CATEGORIES.items():
            if any(kw in lower_task for kw in info["keywords"]):
                matched_category = cat_name
                # Choose the primary query from the category
                query = info["github_queries"][0]
                return query, matched_category

        # Fallback to sanitized keywords
        sanitized = re.sub(r'[^a-zA-Z0-9\s_-]', '', lower_task)
        words = [w for w in sanitized.split() if len(w) > 2 and w not in ["find", "tool", "automatic", "clone", "task", "perform"]]
        query = " ".join(words[:4]) + " security" if words else "security tool"
        return query, matched_category

    def search_tools(self, task_keywords: str, language: Optional[str] = None, min_stars: int = 20, limit: int = 5) -> List[Dict]:
        """Search GitHub for security repositories"""
        query, category = self._build_search_query(task_keywords)
        if language:
            query += f" language:{language}"

        print(Colors.info(f"Querying GitHub for task '{task_keywords}' (query: '{query}', category: '{category}')..."))

        if not REQUESTS_AVAILABLE:
            print(Colors.warning("Python 'requests' package not available. Falling back to predefined tool registry."))
            return self._fallback_known_tools(category)

        try:
            url = f"{self.api_base}/search/repositories"
            params = {
                "q": f"{query} stars:>={min_stars}",
                "sort": "stars",
                "order": "desc",
                "per_page": limit
            }
            res = requests.get(url, headers=self._get_headers(), params=params, timeout=12)

            if res.status_code == 200:
                data = res.json()
                items = data.get("items", [])
                results = []
                for item in items:
                    results.append({
                        "name": item.get("name"),
                        "full_name": item.get("full_name"),
                        "description": item.get("description") or "No description provided.",
                        "stars": item.get("stargazers_count", 0),
                        "language": item.get("language") or "Unknown",
                        "clone_url": item.get("clone_url"),
                        "html_url": item.get("html_url"),
                        "default_branch": item.get("default_branch", "main"),
                        "topics": item.get("topics", []),
                        "category": category
                    })
                return results
            elif res.status_code == 403:
                print(Colors.warning("GitHub API rate limit exceeded. Falling back to known tools."))
                return self._fallback_known_tools(category)
            else:
                print(Colors.error(f"GitHub Search API returned status {res.status_code}: {res.text[:120]}"))
                return self._fallback_known_tools(category)

        except Exception as e:
            print(Colors.error(f"Error connecting to GitHub: {e}"))
            return self._fallback_known_tools(category)

    def _fallback_known_tools(self, category: str) -> List[Dict]:
        """Returns reputable repos from verified catalog if offline or API limited"""
        fallbacks = {
            "sql_injection": [{
                "name": "sqlmap",
                "full_name": "sqlmapproject/sqlmap",
                "description": "Automatic SQL injection and database takeover tool",
                "stars": 33000,
                "language": "Python",
                "clone_url": "https://github.com/sqlmapproject/sqlmap.git",
                "html_url": "https://github.com/sqlmapproject/sqlmap",
                "category": category
            }],
            "web_fuzzing": [{
                "name": "dirsearch",
                "full_name": "maurosoria/dirsearch",
                "description": "Web path scanner",
                "stars": 12000,
                "language": "Python",
                "clone_url": "https://github.com/maurosoria/dirsearch.git",
                "html_url": "https://github.com/maurosoria/dirsearch",
                "category": category
            }],
            "subdomain_enumeration": [{
                "name": "Sublist3r",
                "full_name": "aboul3la/Sublist3r",
                "description": "Fast subdomains enumeration tool for penetration testers",
                "stars": 9000,
                "language": "Python",
                "clone_url": "https://github.com/aboul3la/Sublist3r.git",
                "html_url": "https://github.com/aboul3la/Sublist3r",
                "category": category
            }],
            "xss_scanning": [{
                "name": "XSStrike",
                "full_name": "s0md3v/XSStrike",
                "description": "Most advanced XSS scanner suite",
                "stars": 14000,
                "language": "Python",
                "clone_url": "https://github.com/s0md3v/XSStrike.git",
                "html_url": "https://github.com/s0md3v/XSStrike",
                "category": category
            }],
            "jwt_attacks": [{
                "name": "jwt_tool",
                "full_name": "ticarpi/jwt_tool",
                "description": "A toolkit for validating, forging, scanning and cracking JWTs",
                "stars": 4800,
                "language": "Python",
                "clone_url": "https://github.com/ticarpi/jwt_tool.git",
                "html_url": "https://github.com/ticarpi/jwt_tool",
                "category": category
            }],
            "osint_recon": [{
                "name": "theHarvester",
                "full_name": "laramies/theHarvester",
                "description": "E-mails, subdomains and names Harvester",
                "stars": 6000,
                "language": "Python",
                "clone_url": "https://github.com/laramies/theHarvester.git",
                "html_url": "https://github.com/laramies/theHarvester",
                "category": category
            }]
        }
        return fallbacks.get(category, [{
            "name": "SecLists",
            "full_name": "danielmiessler/SecLists",
            "description": "Security Tester's Companion wordlists and collections",
            "stars": 54000,
            "language": "Python",
            "clone_url": "https://github.com/danielmiessler/SecLists.git",
            "html_url": "https://github.com/danielmiessler/SecLists",
            "category": category
        }])


class ToolRegistry:
    """Tracks discovered, cloned, and installed tools in a local SQLite database"""

    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            base_dir = Path.home() / ".parrotsec_tools"
            base_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(base_dir / "tools_registry.db")
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                repo_url TEXT,
                clone_url TEXT,
                description TEXT,
                stars INTEGER,
                language TEXT,
                category TEXT,
                install_path TEXT,
                executable_path TEXT,
                install_method TEXT,
                installed_at TEXT,
                last_used TEXT,
                use_count INTEGER DEFAULT 0,
                status TEXT
            )
        """)
        conn.commit()
        conn.close()

    def register_tool(self, tool_data: Dict) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO tools (
                    name, repo_url, clone_url, description, stars, language,
                    category, install_path, executable_path, install_method,
                    installed_at, last_used, use_count, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tool_data.get("name"),
                tool_data.get("repo_url"),
                tool_data.get("clone_url"),
                tool_data.get("description"),
                tool_data.get("stars", 0),
                tool_data.get("language"),
                tool_data.get("category", "general"),
                tool_data.get("install_path"),
                tool_data.get("executable_path"),
                tool_data.get("install_method"),
                tool_data.get("installed_at") or time.strftime("%Y-%m-%d %H:%M:%S"),
                tool_data.get("last_used") or time.strftime("%Y-%m-%d %H:%M:%S"),
                tool_data.get("use_count", 1),
                tool_data.get("status", "installed")
            ))
            conn.commit()
            return True
        except Exception as e:
            print(Colors.error(f"Failed to register tool in DB: {e}"))
            return False
        finally:
            conn.close()

    def get_tool(self, name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tools WHERE LOWER(name) = LOWER(?)", (name,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def search_registry(self, keyword: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        pattern = f"%{keyword}%"
        cursor.execute("""
            SELECT * FROM tools 
            WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
            ORDER BY use_count DESC
        """, (pattern, pattern, pattern))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def record_usage(self, name: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tools SET 
                use_count = use_count + 1,
                last_used = ?
            WHERE LOWER(name) = LOWER(?)
        """, (time.strftime("%Y-%m-%d %H:%M:%S"), name))
        conn.commit()
        conn.close()

    def list_all(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tools ORDER BY last_used DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows


class ToolInstaller:
    """Clones security tool repositories and handles dependency setups automatically"""

    def __init__(self, tools_dir: Optional[str] = None):
        if not tools_dir:
            self.tools_dir = Path.home() / ".parrotsec_tools"
        else:
            self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(parents=True, exist_ok=True)

    def is_installed(self, tool_name: str) -> bool:
        dest = self.tools_dir / tool_name
        return dest.exists() and (dest / ".git").exists()

    def get_install_path(self, tool_name: str) -> Path:
        return self.tools_dir / tool_name

    def clone_repository(self, clone_url: str, tool_name: str) -> Optional[Path]:
        """Clones a repo via git or updates if existing"""
        dest_dir = self.tools_dir / tool_name

        if dest_dir.exists():
            print(Colors.info(f"Directory {dest_dir} already exists. Attempting git pull..."))
            try:
                subprocess.run(
                    ["git", "-C", str(dest_dir), "pull"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False
                )
                return dest_dir
            except Exception as e:
                print(Colors.warning(f"Could not update existing repo: {e}"))
                return dest_dir

        print(Colors.c(f"Cloning {clone_url} into {dest_dir}...", Colors.BRIGHT_CYAN))
        try:
            cmd = ["git", "clone", "--depth", "1", clone_url, str(dest_dir)]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                print(Colors.success(f"Cloned repository {tool_name} successfully."))
                return dest_dir
            else:
                print(Colors.warning(f"Git clone exited ({res.returncode}): {res.stderr.strip()}"))
                return self._download_and_extract_zip(clone_url, tool_name, dest_dir)
        except FileNotFoundError:
            print(Colors.warning("Git binary not found in PATH. Falling back to HTTP zip archive download..."))
            return self._download_and_extract_zip(clone_url, tool_name, dest_dir)
        except Exception as e:
            print(Colors.warning(f"Git clone encountered exception: {e}. Falling back to zip download..."))
            return self._download_and_extract_zip(clone_url, tool_name, dest_dir)

    def _download_and_extract_zip(self, clone_url: str, tool_name: str, dest_dir: Path) -> Optional[Path]:
        """Fallback to download zip directly from GitHub if git command is unavailable"""
        import zipfile
        import io
        import urllib.request

        # Convert git clone url to zip download url:
        # https://github.com/sqlmapproject/sqlmap.git -> https://github.com/sqlmapproject/sqlmap/archive/refs/heads/master.zip
        base_url = clone_url.replace(".git", "")
        branches = ["master", "main"]

        for branch in branches:
            zip_url = f"{base_url}/archive/refs/heads/{branch}.zip"
            print(Colors.info(f"Downloading tool archive: {zip_url}..."))
            try:
                req = urllib.request.Request(
                    zip_url,
                    headers={"User-Agent": "ParrotSec-AI-Engine/5.5"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    if resp.status == 200:
                        content = resp.read()
                        with zipfile.ZipFile(io.BytesIO(content)) as zf:
                            # Extract into a temp folder first to get clean top-level
                            extract_tmp = dest_dir.parent / f"{tool_name}_tmp"
                            if extract_tmp.exists():
                                shutil.rmtree(extract_tmp, ignore_errors=True)
                            zf.extractall(extract_tmp)

                            # Find inner folder
                            extracted_subdirs = [p for p in extract_tmp.iterdir() if p.is_dir()]
                            if extracted_subdirs:
                                if dest_dir.exists():
                                    shutil.rmtree(dest_dir, ignore_errors=True)
                                shutil.move(str(extracted_subdirs[0]), str(dest_dir))
                                shutil.rmtree(extract_tmp, ignore_errors=True)
                            else:
                                shutil.move(str(extract_tmp), str(dest_dir))

                            print(Colors.success(f"Tool {tool_name} downloaded and extracted successfully."))
                            return dest_dir
            except Exception as e:
                continue

        print(Colors.error(f"Failed to auto-download zip for {tool_name}. On Parrot OS run: sudo apt install git"))
        return None

    def detect_install_strategy(self, repo_path: Path) -> Dict[str, Any]:
        """Inspects repository contents to deduce installation and execution method"""
        strategy = {
            "type": "direct_python",
            "setup_commands": [],
            "entrypoint": None
        }

        files = [f.name.lower() for f in repo_path.iterdir() if f.is_file()]

        # Check Python setup
        pip_flags = ["--break-system-packages"] if sys.platform != "win32" else []
        if "requirements.txt" in files:
            strategy["type"] = "python_requirements"
            strategy["setup_commands"].append([sys.executable, "-m", "pip", "install", *pip_flags, "-r", "requirements.txt"])
        elif "setup.py" in files:
            strategy["type"] = "python_setup"
            strategy["setup_commands"].append([sys.executable, "-m", "pip", "install", *pip_flags, "-e", "."])
        elif "pyproject.toml" in files:
            strategy["type"] = "python_flit_or_poetry"
            strategy["setup_commands"].append([sys.executable, "-m", "pip", "install", *pip_flags, "."])

        # Check Go
        if "go.mod" in files:
            strategy["type"] = "golang"
            strategy["setup_commands"].append(["go", "build", "-o", f"{repo_path.name}_bin"])

        # Check Rust
        if "cargo.toml" in files:
            strategy["type"] = "cargo"
            strategy["setup_commands"].append(["cargo", "build", "--release"])

        # Check Makefile
        if "makefile" in files:
            strategy["type"] = "make"
            strategy["setup_commands"].append(["make"])

        # Search for executable entrypoints
        # 1. Look for python script matching repo name
        candidates = [
            f"{repo_path.name.lower()}.py",
            "main.py",
            "run.py",
            "cli.py",
            f"{repo_path.name.lower()}",
        ]
        found_entry = None
        for cand in candidates:
            cand_path = repo_path / cand
            if cand_path.is_file():
                found_entry = str(cand_path)
                try:
                    os.chmod(cand_path, os.stat(cand_path).st_mode | 0o755)
                except Exception:
                    pass
                break

        if not found_entry:
            # Look for any top-level executable .py file
            py_files = list(repo_path.glob("*.py"))
            if py_files:
                # Prefer one with 'scan' or 'main' in name or biggest file
                py_files.sort(key=lambda p: (not ("main" in p.name or "cli" in p.name), -p.stat().st_size))
                found_entry = str(py_files[0])
                try:
                    os.chmod(py_files[0], os.stat(py_files[0]).st_mode | 0o755)
                except Exception:
                    pass

        strategy["entrypoint"] = found_entry
        return strategy

    def install_dependencies(self, repo_path: Path, strategy: Dict[str, Any]) -> bool:
        """Executes setup commands to install dependencies with Parrot OS / Debian PEP-668 fallback"""
        commands = strategy.get("setup_commands", [])
        if not commands:
            return True

        for cmd in commands:
            print(Colors.info(f"Running auto-install: {' '.join(cmd)} in {repo_path.name}..."))
            try:
                res = subprocess.run(
                    cmd,
                    cwd=str(repo_path),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=180
                )
                if res.returncode != 0:
                    # If failed because --break-system-packages is unrecognized on older pip
                    if "--break-system-packages" in cmd:
                        alt_cmd = [c for c in cmd if c != "--break-system-packages"]
                        print(Colors.info(f"Retrying install without --break-system-packages: {' '.join(alt_cmd)}..."))
                        alt_res = subprocess.run(alt_cmd, cwd=str(repo_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
                        if alt_res.returncode == 0:
                            print(Colors.success("Dependency step succeeded."))
                            continue
                    # If failed because externally-managed-environment on Debian/Parrot
                    elif "externally-managed-environment" in res.stderr and "--break-system-packages" not in cmd:
                        alt_cmd = cmd[:4] + ["--break-system-packages"] + cmd[4:]
                        print(Colors.info(f"Retrying install with --break-system-packages for Parrot OS: {' '.join(alt_cmd)}..."))
                        alt_res = subprocess.run(alt_cmd, cwd=str(repo_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=180)
                        if alt_res.returncode == 0:
                            print(Colors.success("Dependency step succeeded."))
                            continue
                    print(Colors.warning(f"Install warning ({res.returncode}): {res.stderr[:200]}"))
                else:
                    print(Colors.success(f"Dependency step succeeded."))
            except Exception as e:
                print(Colors.error(f"Install error: {e}"))
                return False
        return True


class AutoToolResolver:
    """The central Autonomous Engine that finds, installs, and executes tools for any requested task"""

    def __init__(self, github_token: Optional[str] = None):
        self.finder = GitHubToolFinder(github_token)
        self.registry = ToolRegistry()
        self.installer = ToolInstaller()

    def autonomous_resolve_and_execute(
        self,
        task_prompt: str,
        target: str,
        custom_args: str = "",
        auto_approve: bool = True
    ) -> Dict[str, Any]:
        """
        Main autonomous pipeline:
        1. Identify the task category and required tool capability.
        2. Check if a suitable tool is already installed in the system or ~/.parrotsec_tools registry.
        3. If not, auto-search GitHub for the top-rated security repo for that task.
        4. Clone repository into local toolchain and build its dependencies.
        5. Discern the CLI invocation syntax and launch it against the target!
        """
        print(Colors.header("\n🤖 AUTONOMOUS TOOL DISCOVERY & EXECUTION PIPELINE"))
        print(Colors.c(f"🎯 Target: {target} | Task: '{task_prompt}'", Colors.BOLD + Colors.BRIGHT_WHITE))

        # 1. First check if a native tool for this task is already present in Parrot OS / Linux PATH
        query, category = self.finder._build_search_query(task_prompt)
        cat_info = TOOL_CATEGORIES.get(category, {})
        candidates_to_check = list(cat_info.get("known_tools", []))
        first_token = task_prompt.strip().split()[0].lower()
        if shutil.which(first_token) and first_token not in candidates_to_check:
            candidates_to_check.insert(0, first_token)

        for kt in candidates_to_check:
            sys_path = shutil.which(kt)
            if sys_path:
                print(Colors.success(f"Parrot OS native tool '{kt}' detected in PATH: {sys_path}"))
                return self._execute_tool({
                    "name": kt,
                    "repo_url": "system",
                    "install_path": os.path.dirname(sys_path) or ".",
                    "executable_path": sys_path,
                    "category": category,
                    "status": "system"
                }, target, task_prompt, custom_args)

        # 2. Check existing local tool registry
        matches = self.registry.search_registry(task_prompt)
        tool_to_use = None

        if matches and Path(matches[0].get("install_path", "")).exists():
            tool_to_use = matches[0]
            print(Colors.success(f"Found ready-to-use local tool from registry: '{tool_to_use['name']}'"))
        else:
            # Search GitHub
            discovered = self.finder.search_tools(task_prompt, min_stars=20, limit=3)
            if not discovered:
                return {
                    "success": False,
                    "error": f"No suitable security tools found on GitHub for task: '{task_prompt}'"
                }

            best_candidate = discovered[0]
            print(Colors.c(f"\n🌟 Top GitHub match identified:", Colors.BRIGHT_YELLOW))
            print(f"   Name: {best_candidate['name']} ({best_candidate['stars']} ⭐)")
            print(f"   Description: {best_candidate['description']}")
            print(f"   URL: {best_candidate['html_url']}")

            # Clone and install
            clone_path = self.installer.clone_repository(
                best_candidate["clone_url"],
                best_candidate["name"]
            )
            if not clone_path:
                return {"success": False, "error": "Failed to clone repository from GitHub"}

            strategy = self.installer.detect_install_strategy(clone_path)
            self.installer.install_dependencies(clone_path, strategy)

            tool_info = {
                "name": best_candidate["name"],
                "repo_url": best_candidate["html_url"],
                "clone_url": best_candidate["clone_url"],
                "description": best_candidate["description"],
                "stars": best_candidate["stars"],
                "language": best_candidate["language"],
                "category": best_candidate.get("category", "general"),
                "install_path": str(clone_path),
                "executable_path": strategy.get("entrypoint") or str(clone_path),
                "install_method": strategy.get("type", "direct"),
                "status": "ready"
            }
            self.registry.register_tool(tool_info)
            tool_to_use = tool_info

        # Execute tool
        return self._execute_tool(tool_to_use, target, task_prompt, custom_args)

    def _execute_tool(self, tool_info: Dict, target: str, task: str, custom_args: str) -> Dict[str, Any]:
        """Runs the tool with appropriate syntax"""
        install_path = Path(tool_info.get("install_path", "."))
        entrypoint = tool_info.get("executable_path")

        if not entrypoint or not Path(entrypoint).exists():
            # Try to find entrypoint now
            strategy = self.installer.detect_install_strategy(install_path)
            entrypoint = strategy.get("entrypoint")

        if not entrypoint:
            return {
                "success": False,
                "error": f"Could not determine entrypoint for tool {tool_info['name']}"
            }

        # Build command based on tool type and entrypoint
        cmd_parts = []
        if entrypoint.endswith(".py"):
            cmd_parts.extend([sys.executable, entrypoint])
        elif os.access(entrypoint, os.X_OK):
            cmd_parts.append(entrypoint)
        else:
            cmd_parts.extend([sys.executable, entrypoint])

        # Infer standard target flags based on tool heuristics
        tool_name = tool_info["name"].lower()
        if "sqlmap" in tool_name:
            cmd_parts.extend(["-u", target, "--batch"])
        elif "dirsearch" in tool_name or "ffuf" in tool_name:
            cmd_parts.extend(["-u", target])
        elif "sublist3r" in tool_name or "subfinder" in tool_name:
            cmd_parts.extend(["-d", target])
        elif "xsstrike" in tool_name:
            cmd_parts.extend(["-u", target])
        elif "theharvester" in tool_name:
            cmd_parts.extend(["-d", target, "-b", "all"])
        elif "nuclei" in tool_name:
            cmd_parts.extend(["-u", target])
        else:
            # Default target placement
            cmd_parts.append(target)

        if custom_args:
            cmd_parts.extend(shlex.split(custom_args))

        full_cmd_str = " ".join(cmd_parts)
        print(Colors.c(f"\n🚀 Running Autonomous Tool Command:\n   $ {full_cmd_str}\n", Colors.BOLD + Colors.BRIGHT_GREEN))

        start_time = time.time()
        try:
            proc = subprocess.Popen(
                cmd_parts,
                cwd=str(install_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(timeout=240)
            duration = time.time() - start_time

            self.registry.record_usage(tool_info["name"])

            success = proc.returncode == 0 or (len(stdout) > 50 and "Traceback" not in stdout)

            if stdout:
                print(stdout[:2500])
                if len(stdout) > 2500:
                    print(Colors.DIM + f"... [truncated {len(stdout) - 2500} bytes of output]" + Colors.RESET)

            if proc.returncode != 0 and stderr:
                print(Colors.warning(f"Standard Error:\n{stderr[:800]}"))

            return {
                "success": success,
                "tool_name": tool_info["name"],
                "command": full_cmd_str,
                "output": stdout,
                "error": stderr,
                "duration": duration,
                "exit_code": proc.returncode
            }
        except subprocess.TimeoutExpired:
            proc.kill()
            print(Colors.error("Autonomous tool execution timed out (limit: 240s)"))
            return {
                "success": False,
                "tool_name": tool_info["name"],
                "command": full_cmd_str,
                "error": "Timeout expired",
                "exit_code": -1
            }
        except Exception as e:
            print(Colors.error(f"Failed to execute autonomous tool: {e}"))
            return {
                "success": False,
                "tool_name": tool_info["name"],
                "command": full_cmd_str,
                "error": str(e),
                "exit_code": -1
            }
