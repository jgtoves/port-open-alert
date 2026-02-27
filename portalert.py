import psutil
import time
from datetime import datetime

def get_open_ports():
    """Returns a set of currently open listening ports."""
    ports = set()
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN':
            ports.add((conn.laddr.port, conn.pid))
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
