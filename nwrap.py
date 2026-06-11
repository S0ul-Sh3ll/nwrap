#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import tempfile
import re
from datetime import datetime

# Global config for profiles (Shared between kali and root)
CONFIG_FILE = "/etc/nwrap_profiles.json"
# Session config (Tied to terminal PID and specific User ID to prevent permission clashes)
SESSION_TARGET_FILE = os.path.join(tempfile.gettempdir(), f"nwrap_session_{os.getuid()}.json")

# The default profile
DEFAULT_CONFIG = {
    "profiles": {
        "ctf-tcp": "-p- -Pn -A --min-rate 2000 --initial-rtt-timeout 50ms --max-rtt-timeout 150ms --max-retries 1 --open"
    }
}

def print_banner():
    banner = r"""
  _   _  __        __  ____       _      ____  
 | \ | | \ \      / / |  _ \     / \    |  _ \ 
 |  \| |  \ \ /\ / /  | |_) |   / _ \   | |_) |
 | |\  |   \ V  V /   |  _ <   / ___ \  |  __/ 
 |_| \_|    \_/\_/    |_| \_\ /_/   \_\ |_|    
                                               
    """
    print("\033[96m" + banner + "\033[0m")
    print("\033[93m[>] Made by: Rishabh Dahiya\033[0m")
    print("\033[93m[>] GitHub: https://github.com/S0ul-Sh3ll\033[0m")
    print("\033[91m[!] DISCLAIMER: This is a personal utility intended for individual use.\n    Use responsibly and entirely at your own risk.\033[0m")
    print("-" * 65 + "\n")

def load_config():
    """Loads the global profiles."""
    if not os.path.exists(CONFIG_FILE):
        # Try to create the global file. If run as normal user, it will silently 
        # fail and just use the defaults in memory until root runs it.
        try:
            with open(CONFIG_FILE, "w") as file:
                json.dump(DEFAULT_CONFIG, file, indent=4)
        except PermissionError:
            pass
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    """Saves profiles globally. Requires sudo."""
    try:
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
    except PermissionError:
        print("\n[-] Permission Denied: Profiles are now shared globally.")
        print("[!] You must use 'sudo' to add, edit, or delete profiles.")
        print("    Example: sudo nwrap add stealth -sS -Pn\n")
        sys.exit(1)

def get_active_target():
    """Checks $target env variable first, then the session-tied file."""
    env_target = os.environ.get("target") or os.environ.get("TARGET")
    if env_target:
        return env_target, "Environment Variable ($target)"
    
    if os.path.exists(SESSION_TARGET_FILE):
        try:
            with open(SESSION_TARGET_FILE, "r") as f:
                data = json.load(f)
                saved_ppid = data.get("ppid")
                
                if os.path.exists(f"/proc/{saved_ppid}"):
                    return data.get("target"), "Current Terminal Session"
                else:
                    os.remove(SESSION_TARGET_FILE)
        except (json.JSONDecodeError, OSError):
            pass 
            
    return None, "None"

def save_session_target(ip):
    """Saves the target tied strictly to the current terminal's Process ID."""
    data = {
        "target": ip,
        "ppid": os.getppid() 
    }
    with open(SESSION_TARGET_FILE, "w") as f:
        json.dump(data, f)

def run_scan_with_progress(nmap_cmd):
    """Executes Nmap and parses its output to draw a live progress bar."""
    cmd = nmap_cmd[:1] + ["--stats-every", "2s"] + nmap_cmd[1:]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    print("\n" + "="*55)
    
    for line in process.stdout:
        if "% done" in line:
            phase_name = "Scan"
            phase_match = re.search(r'^\s*(.*?)\s*Timing:', line)
            if phase_match:
                phase_name = phase_match.group(1).strip()

            match = re.search(r'(\d+(?:\.\d+)?)%\s*done', line)
            if match:
                pct = float(match.group(1))
                bar_len = 30
                filled = int(bar_len * (pct / 100.0))
                bar = '█' * filled + '-' * (bar_len - filled)
                sys.stdout.write(f"\r\033[K\033[92m[+] {phase_name}: [{bar}] {pct:.2f}%\033[0m")
                sys.stdout.flush()
        
        elif line.startswith("Stats: ") or "elapsed;" in line:
            continue
            
        else:
            sys.stdout.write(f"\r\033[K{line}")
            sys.stdout.flush()
            
    process.wait()
    
    sys.stdout.write("\r\033[K")
    print("="*55)

def main():
    if len(sys.argv) < 2:
        print_banner()
        print("Usage: nwrap <action> [value]")
        print("\nCommands:")
        print("  ls                        List profiles and active target")
        print("  target=<ip>               Set target (Resets when terminal closes)")
        print("  scan <profile>            Run a scan against the target")
        print("\nProfile Management:")
        print("  add <name> <flags>        Add a new profile (Requires sudo)")
        print("                            Example: sudo nwrap add stealth -sS -Pn -T2")
        print("  edit <name> <new flags>   Edit an existing profile (Requires sudo)")
        print("  delete <name>             Delete a profile (Requires sudo)")
        print("\nOutput:")
        print("  * All scans are automatically saved in the current working directory")
        print("    in all Nmap formats (-oA) as: <target_ip>_<date>_<time>.*")
        print("-" * 65)
        sys.exit(1)

    action_arg = sys.argv[1]
    value = sys.argv[2] if len(sys.argv) > 2 else None
    
    if value and len(sys.argv) > 3 and action_arg not in ["add", "edit"]:
        value = " ".join(sys.argv[2:])

    config = load_config()

    if action_arg.startswith("target="):
        new_target = action_arg.split("=", 1)[1].strip()
        if not new_target:
            print("[-] Error: Please provide an IP. Example: nwrap target=192.168.1.1")
            return
        save_session_target(new_target)
        print(f"[+] Success! Target set to {new_target} for this terminal session.")
        return

    elif action_arg == "ls":
        print_banner()
        active_ip, source = get_active_target()
        print(f"[i] Current Target: {active_ip if active_ip else 'None set'} (Source: {source})\n")
        print("[i] Available Profiles:")
        for name, flags in config["profiles"].items():
            print(f"  - {name}: {flags}")

    elif action_arg == "add":
        if len(sys.argv) < 4:
            print("[-] Error: Use format: sudo nwrap add <name> <flags>")
            return
        name = sys.argv[2].strip()
        flags = " ".join(sys.argv[3:]).strip('"\'') 
        config["profiles"][name] = flags
        save_config(config)
        print(f"[+] Success! Profile '{name}' added with flags: {flags}")

    elif action_arg == "edit":
        if len(sys.argv) < 4:
            print("[-] Error: Use format: sudo nwrap edit <name> <new flags>")
            return
        name = sys.argv[2].strip()
        flags = " ".join(sys.argv[3:]).strip('"\'')
        
        if name not in config["profiles"]:
            print(f"[-] Error: Profile '{name}' does not exist.")
            return
            
        config["profiles"][name] = flags
        save_config(config)
        print(f"[+] Success! Profile '{name}' updated to: {flags}")

    elif action_arg == "delete":
        if not value:
            print("[-] Error: Provide a profile name to delete.")
            return
        name = value.strip()
        if name not in config["profiles"]:
            print(f"[-] Error: Profile '{name}' not found.")
            return
            
        choice = input(f"[!] Are you sure you want to delete profile '{name}'? (y/n): ").strip().lower()
        if choice == 'y':
            del config["profiles"][name]
            save_config(config)
            print(f"[+] Profile '{name}' deleted permanently.")
        else:
            print("[-] Deletion aborted.")

    elif action_arg == "scan":
        print_banner()
        if not value:
            print("[-] Error: Please provide a profile. Example: nwrap scan ctf-tcp")
            return

        profile_name = value.strip()
        if profile_name not in config["profiles"]:
            print(f"[-] Error: Profile '{profile_name}' not found. Use 'ls' to view profiles.")
            return

        target_ip, source = get_active_target()
        
        if not target_ip:
            target_ip = input("[?] No target set. Please enter an IP to scan: ")
            save_session_target(target_ip)
            print(f"[+] Target saved as {target_ip} for this terminal session.\n")

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_name = f"{target_ip}_{now}"
        out_path = os.path.join(os.getcwd(), out_name)

        flags = config["profiles"][profile_name]
        nmap_cmd = ["nmap"] + flags.split() + ["-oA", out_path, target_ip]
        cmd_str = " ".join(nmap_cmd)

        print(f"[*] Target: {target_ip}")
        print(f"[*] Output: {out_path}.[nmap|gnmap|xml]")
        print(f"[*] Command:\n    {cmd_str}\n")
        
        choice = input("[?] Do you want to proceed? (y/n): ").strip().lower()

        if choice != 'y':
            print("[-] Scan aborted.")
            return

        print(f"\n[+] Executing profile '{profile_name}'...")
        try:
            run_scan_with_progress(nmap_cmd)
            print(f"\n[+] Scan complete! Results saved as: {out_name}.*")
        except FileNotFoundError:
            print("[-] Error: 'nmap' does not seem to be installed or is not in your PATH.")
        except KeyboardInterrupt:
            sys.stdout.write("\r\033[K")
            print("\n[-] Scan cancelled by user.")

    else:
        print(f"[-] Unknown command: {action_arg}. Type 'nwrap' without arguments for usage.")

if __name__ == "__main__":
    main()
