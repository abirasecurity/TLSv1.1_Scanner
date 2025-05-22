import subprocess
import concurrent.futures
import os
import re
import threading
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

# Add a lock for synchronized printing
print_lock = threading.Lock()

DEFAULT_PORT = 443

def parse_target_line(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if ':' in line:
        ip, port = line.split(':')
        return ip.strip(), int(port.strip())
    else:
        return line.strip(), DEFAULT_PORT

def check_tls11(ip, port):
    try:
        # Use the lock when printing to prevent output jumbling
        with print_lock:
            print(f"{Fore.CYAN}[+] Scanning {ip}:{port}")

        result = subprocess.run(
            ["sslscan", "--no-colour", f"{ip}:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        output = result.stdout

        # Look for the exact line indicating TLSv1.1 is enabled
        if "TLSv1.1   enabled" in output:
            with print_lock:
                print(f"{Fore.YELLOW}[!] TLSv1.1 ENABLED on {ip}:{port}")
            return (ip, port, True)
        else:
            return (ip, port, False)

    except Exception as e:
        with print_lock:
            print(f"{Fore.RED}[!] Error scanning {ip}:{port}: {e}")
        return (ip, port, None)

def load_targets(filename):
    targets = []
    with open(filename, 'r') as f:
        for line in f:
            parsed = parse_target_line(line)
            if parsed:
                targets.append(parsed)
    return targets

def print_basic_results(all_results):
    # Filter results to get only vulnerable hosts
    vulnerable_hosts = [(ip, port) for ip, port, is_vulnerable in all_results if is_vulnerable is True]
    non_vulnerable_hosts = [(ip, port) for ip, port, is_vulnerable in all_results if is_vulnerable is False]

    print(f"\n{Fore.CYAN}{Style.BRIGHT}[✓] Scan Results:\n")

    if vulnerable_hosts:
        print(f"{Fore.YELLOW}{Style.BRIGHT}[!] Hosts with TLSv1.1 ENABLED:\n")
        for ip, port in vulnerable_hosts:
            print(f"{Fore.YELLOW}    - {ip}:{port}")
    else:
        print(f"{Fore.GREEN}{Style.BRIGHT}[✓] No hosts were found with TLSv1.1 enabled.")

    if non_vulnerable_hosts:
        print(f"\n{Fore.GREEN}[+] Hosts with TLSv1.1 DISABLED:\n")
        for ip, port in non_vulnerable_hosts:
            print(f"{Fore.GREEN}    - {ip}:{port}")

def print_remediation_results(all_results):
    # Separate vulnerable and remediated hosts
    vulnerable_hosts = []
    remediated_hosts = []

    for ip, port, is_vulnerable in all_results:
        if is_vulnerable is True:
            vulnerable_hosts.append((ip, port))
        elif is_vulnerable is False:  # Only count as remediated if we got a valid False result
            remediated_hosts.append((ip, port))

    # Print summary
    print(f"\n{Fore.CYAN}{Style.BRIGHT}[✓] Remediation Test Results:\n")

    if vulnerable_hosts:
        print(f"{Fore.YELLOW}{Style.BRIGHT}[!] Hosts with TLSv1.1 still ENABLED:\n")
        for ip, port in vulnerable_hosts:
            print(f"{Fore.YELLOW}    {ip}:{port} - {Fore.RED}{Style.BRIGHT}NOT REMEDIATED")

    if remediated_hosts:
        print(f"\n{Fore.GREEN}[+] Hosts with TLSv1.1 disabled:\n")
        for ip, port in remediated_hosts:
            print(f"{Fore.GREEN}    {ip}:{port} - {Fore.GREEN}{Style.BRIGHT}REMEDIATED")

    # Print overall statistics
    print(f"\n{Fore.CYAN}[*] Total hosts scanned: {len(all_results)}")
    print(f"{Fore.YELLOW}[*] Hosts with TLSv1.1 enabled: {len(vulnerable_hosts)}")
    print(f"{Fore.GREEN}[*] Hosts with TLSv1.1 disabled: {len(remediated_hosts)}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Detect TLSv1.1 Support using sslscan")
    parser.add_argument("-i", "--input", required=True, help="Input file with IP[:port] targets")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of concurrent threads (default: 10)")
    parser.add_argument("-r", "--remediation_test", action="store_true", 
                        help="Run in remediation test mode (shows REMEDIATED/NOT REMEDIATED status)")
    args = parser.parse_args()

    targets = load_targets(args.input)

    with print_lock:
        print(f"{Fore.CYAN}[+] Loaded {len(targets)} targets from {args.input}")

    all_results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = [executor.submit(check_tls11, ip, port) for ip, port in targets]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:  # Only add valid results (not None)
                all_results.append(res)

    # Check for any hosts that failed to scan
    failed_count = len(targets) - len(all_results)
    if failed_count > 0:
        with print_lock:
            print(f"{Fore.RED}[!] Warning: {failed_count} hosts failed to scan properly")

    # Display results based on selected mode
    if args.remediation_test:
        print_remediation_results(all_results)
    else:
        print_basic_results(all_results)
