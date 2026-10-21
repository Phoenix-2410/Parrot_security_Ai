# 🦜 ParrotSec AI Assistant

An AI-inspired, terminal-based security assistant for **Parrot Security OS, Kali Linux, and other Linux security labs**. It brings common security workflows, tool management, plugins, scan history, and optional threat-intelligence integrations into one command-line interface.

> **Use only on systems, applications, and networks you own or have explicit permission to test.**

## ✨ Features

- **Security workflow support** — organize reconnaissance and web-audit tasks into repeatable workflows.
- **Tool discovery and registry** — discover and manage compatible open-source security tools, where supported.
- **Reconnaissance helpers** — run supported scans and follow-up checks against authorized targets.
- **Findings and reports** — review stored assessment results and generate reports when supported by the selected command.
- **Session management** — preserve assessment information for later review.
- **Plugin system** — extend the assistant with your own Python plugins.
- **Threat-intelligence integrations** — optional Shodan and VirusTotal features using your own API keys.
- **Terminal interface** — interactive commands, colored output, banners, and status feedback.
- **Local storage** — SQLite databases are used for application data and macros.

## 🧰 Requirements

- Python 3.7 or newer
- Parrot Security OS or Kali Linux recommended
- Git, for features that retrieve repositories
- `requests` Python package
- Security tools required by the commands you want to use (for example, Nmap)
- Optional API keys for Shodan and VirusTotal

Some operations may require elevated privileges. Run with the minimum permissions needed.

## 🚀 Installation

### 1. Download the project

Download or clone this repository, then open a terminal in the project directory.

```bash
git clone https://github.com/Phoenix-2410/Parrot_security_Ai.git
cd Parrot_security_Ai
```

If you downloaded a ZIP, extract it and `cd` into the extracted folder instead.

### 2. Install Python dependencies

```bash
python3 -m pip install -r requirements.txt
sudo ./install.sh
```

On Parrot OS or Kali Linux, if the system Python environment is externally managed, use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
sudo ./install.sh
```

### 3. Start the assistant

Run the entry-point script available in this repository:

```
sudo parrot-ai

```

Use `--help` if command-line help is supported by that version. The optional `install.sh` installer may set up a launcher; review the script before running it with `sudo`.

## 💻 Example commands

The exact commands depend on the version and available tools. Examples documented for the assistant include:

```text
target 192.168.1.100
scan 192.168.1.100
smartrecon 192.168.1.100
workflow full_recon 192.168.1.100
workflows
tools
plugins
db
db findings
report pentest.html
```

For autonomous tool discovery, versions that support it may provide commands similar to:

```text
findtool cors scanner
autotool subdomain_enum example.com
```

**Important:** These are examples, not a guarantee that every command is enabled in every version. Check the command help/menu and confirm that the required third-party tool is installed before use.

## 🔑 Optional API integrations

Some threat-intelligence features require API keys.

- [Shodan](https://www.shodan.io/)
- [VirusTotal](https://www.virustotal.com/)

Configure keys using the assistant's supported API settings command, if available in your version. Do not commit API keys, tokens, passwords, or other secrets to GitHub.

## 🔌 Plugin development

Plugins are stored in the `plugins/` directory. Use the example plugin as a starting point and follow the interface expected by the plugin loader in your version.

General development tips:

1. Give the plugin a clear name and description.
2. Validate all input.
3. Use safe subprocess calls and avoid building shell commands from untrusted input.
4. Handle missing dependencies and errors gracefully.
5. Test only in a lab or on authorized targets.

## 📁 Project structure

```text
.
├── parrot_ai.py             # Main assistant script
├── parrot_ai_v5.py          # Newer assistant version
├── parrot-ai                # Launcher, if configured
├── install.sh               # Optional installation script
├── requirements.txt         # Python dependencies
├── plugins/
│   └── example_plugin.py    # Example plugin
├── modules/
│   ├── github_tool_engine.py
│   └── advanced_features.py
├── parrotsec_ai.db          # Local application database
└── parrotsec_macros.db      # Local macro database
```

Database files may contain local history or assessment details. Review them before publishing or sharing a copy of the project.

## 🛡️ Responsible use

This project is intended for **education, defensive security, and authorized security testing**.

- Obtain written permission before testing a third-party system.
- Follow the scope and rules of engagement for each assessment.
- Do not use the tool to access, disrupt, or damage systems without authorization.
- Review commands and third-party tools before executing them.
- You are responsible for complying with applicable laws and policies.

## 🤝 Contributing

Contributions are welcome. Open an issue to report a bug or suggest a feature, or submit a pull request with a clear description and testing notes.

## 📄 Contributing

This project is licensed under the MIT License. See the "LICENSE" (LICENSE.) file for details.

---

**Built for cybersecurity learning and authorized lab work.**
