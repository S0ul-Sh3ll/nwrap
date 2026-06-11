#!/bin/bash

echo -e "\033[96m[*] Starting nwrap installation...\033[0m"

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
  echo -e "\033[91m[-] Please run the installer with sudo: sudo ./install.sh\033[0m"
  exit 1
fi

# Copy the python script to the system path
cp nwrap.py /usr/local/bin/nwrap

# Make it executable
chmod +x /usr/local/bin/nwrap

echo -e "\033[92m[+] Installation Complete!\033[0m"
echo -e "\033[93m[i] Type 'nwrap' in your terminal to view the help menu.\033[0m"
