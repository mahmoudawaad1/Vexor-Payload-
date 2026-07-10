# Vexor Agent

Modular C2 (Command & Control) agent framework for authorized red team operations and penetration testing.

## Architecture

```
vexor/
├── agent.py          # Main agent entry point
├── config.py         # C2 server configuration
├── vexor/
│   ├── c2.py         # Encrypted C2 communication
│   ├── crypto.py     # AES-256-CBC encryption
│   ├── persistence.py # Cross-platform persistence
│   ├── recon.py      # System reconnaissance
│   ├── executor.py   # Command execution
│   ├── exfil.py      # File exfiltration
│   ├── keylogger.py  # Keystroke capture
│   ├── screenshot.py # Screen capture
│   └── evasion.py    # Anti-analysis techniques
└── server/
    └── c2_server.py  # Flask-based C2 server
```

## Features

- AES-256 encrypted C2 channel
- Cross-platform (Windows, Linux, macOS)
- Systemd / LaunchAgent / Registry persistence
- Keystroke logging with platform-specific handlers
- Screenshot capture (pyautogui + fallback)
- File exfiltration with filtering
- Shell, Python, and file operation execution
- VM / sandbox detection
- Anti-debug checks
- Self-destruct capability

## Setup

### 1. Configure Agent

Edit `config.py` with your C2 server IP:

```python
C2_HOST = "YOUR_C2_IP"
C2_PORT = 8443
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start C2 Server

```bash
python server/c2_server.py
```

### 4. Run Agent

```bash
python agent.py
```

### 5. Build Executable (Optional)

```bash
pip install pyinstaller
pyinstaller --onefile --hidden-import=cryptography agent.py
```

## C2 Commands

| Command | Description |
|---------|-------------|
| `shell <cmd>` | Execute shell command |
| `python <code>` | Execute Python code |
| `read <path>` | Read file contents |
| `write <path> <content>` | Write file |
| `download <url> <dest>` | Download file |
| `ls <path>` | List directory |
| `recon` | System reconnaissance |
| `persist` | Install persistence |
| `unpersist` | Remove persistence |
| `keylog_start` | Start keylogger |
| `keylog_stop` | Stop keylogger |
| `keylog_dump` | Dump keystrokes |
| `screenshot` | Capture screen |
| `exfil <paths>` | Exfiltrate files |
| `selfdestruct` | Remove agent |

## Disclaimer

This tool is for authorized security testing only. Unauthorized use is illegal. Always obtain written permission before testing.

## License

MIT
