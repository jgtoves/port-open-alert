import psutil
import time
from datetime import datetime
import subprocess 
import re

def get_open_ports():
    """Returns a set of currently open listening ports using the 'ss' command."""
    ports = set()
    try:
        # Run the 'ss' command: -l (listening), -p (process), -t (tcp), -n (numeric)
        # We use 'su -c' only if rooted, but standard 'ss' usually works for local ports
        result = subprocess.check_output(['ss', '-lptn'], stderr=subprocess.DEVNULL).decode()
        
        # Look for the port number in the output (e.g., 0.0.0.0:8080 or [::]:8080)
        # Regex looks for the colon followed by the port digits
        matches = re.findall(r':(\d+)\s+', result)
        
        for port in matches:
            # We'll use 0 as a placeholder since 'ss' doesn't always show PID without root
            ports.add((int(port), 0)) 
            
    except Exception as e:
        print(f"Extraction Error: {e}")
    return ports

def monitor():
    print("--- PORT SYSTEM ACTIVE ---")
    # Initial scan to set the baseline
    baseline = get_open_ports()
    print(f"[*] Baseline established. Monitoring {len(baseline)} active ports...")

    while True:
        current_ports = get_open_ports()
        
        # Check for new ports
        new_entries = current_ports - baseline
        if new_entries:
            for port, pid in new_entries:
                proc_name = psutil.Process(pid).name() if pid else "Unknown"
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"\n[!!!] SYSTEM ALERT at {timestamp}")
                print(f"[+] NEW PORT OPENED: {port}")
                print(f"[+] PROCESS: {proc_name} (PID: {pid})")
                
                # Update baseline so we don't alert on the same port twice
                baseline.add((port, pid))

        # Check for closed ports
        closed_entries = baseline - current_ports
        if closed_entries:
            for port, pid in closed_entries:
                print(f"[-] Port {port} (PID: {pid}) has been closed.")
                baseline.remove((port, pid))

        time.sleep(2) # Scan every 2 seconds

if __name__ == "__main__":
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n[!] Sentry standing down.")
