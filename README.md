# NWRAP 🕵️‍♂️
**A sleek, automated, and persistent Command-Line Wrapper for Nmap.**

`nwrap` simplifies network reconnaissance by mapping lengthy, complex Nmap commands to easy-to-remember profile names. It features real-time dynamic progress bars, automated output logging, and seamless integration with environment variables.

Created by: **Rishabh Dahiya**

---

## ✨ Features
* **Custom Profiles:** Save complex scans (e.g., `ctf-tcp`) and run them with a single word.
* **Live Progress Tracking:** Replaces messy Nmap stat outputs with a clean, dynamic progress bar that updates based on the specific scan phase (SYN Stealth, OS Detection, etc.).
* **Auto-Logging:** Automatically saves every scan in all formats (`-oA`) in your current working directory, stamped with the target IP, date, and time.
* **Smart Targeting:** Set a persistent target IP for your current terminal session, or seamlessly pull from the `$target` environment variable.
* **Global Configuration:** Profiles are saved securely in `/etc/nwrap_profiles.json`, meaning they are shared seamlessly whether you run scans as a normal user or root.

---

## 🚀 Installation

Clone the repository and run the install script:

```git clone https://github.com/S0ul-Sh3ll/nwrap.git```
```cd nwrap```
```sudo ./install.sh```

---

## 📖 Usage Guide
Running nwrap without arguments will display the help menu.

### 1. Managing Profiles (Requires Sudo)
Because profiles are stored globally, modifying them requires root privileges.
Note: Do NOT include nmap or the target IP in your flags.

### _Add a new profile_
```sudo nwrap add stealth -sS -Pn -T2```

### _Edit an existing profile_
```sudo nwrap edit ctf-tcp -p- -A -T4 -v```

### _Delete a profile_
```sudo nwrap delete stealth```

Either type sudo or open terminal as root to skip typing sudo before nwrap.
Only adding, deleting, editing requires sudo permission.
To scan from available profiles you do not need sudo permission.

### 2. Setting a Target
You can set a target that will persist as long as your terminal remains open:
```nwrap target=10.10.10.5```

<ins>(Alternatively, simply export target=10.10.10.10 in your shell, and nwrap will detect it!)</ins> - #### Recommended

### 3. Running a Scan
Run a scan using your profile name. It will automatically grab your active target and start the progress bar.

```nwrap scan ctf-tcp```

### 4. Listing Data
View your current active target and all saved profiles:

```nwrap ls```

<ins>Disclaimer: This is a personal utility intended for individual use. Use responsibly, legally, and entirely at your own risk.</ins>
