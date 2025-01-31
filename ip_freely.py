import argparse
import ipaddress
import subprocess
import platform
import time
import threading
from concurrent.futures import ThreadPoolExecutor

def ping_host(ip):
    """Pings a host and returns its status and response time."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", "-W", "1", ip]

    try:
        start_time = time.time()
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds

        if result.returncode == 0:
            return ip, "UP", f"{response_time}ms"
        else:
            return ip, "DOWN", "No response"
    except Exception as e:
        return ip, "ERROR", str(e)

def scan_ips(ip_list, max_threads=50):
    """Scans a list of given IP addresses using multithreading."""
    print("\nStarting scan...\n")

    active_hosts = 0
    down_hosts = 0
    error_hosts = 0

    def process_result(result):
        """Processes the result of a ping scan."""
        nonlocal active_hosts, down_hosts, error_hosts
        ip, status, message = result
        print(f"{ip} - {status} ({message})")

        if status == "UP":
            active_hosts += 1
        elif status == "DOWN":
            down_hosts += 1
        else:
            error_hosts += 1

    with ThreadPoolExecutor(max_threads) as executor:
        results = executor.map(ping_host, ip_list)

        for result in results:
            process_result(result)

    print("\nScan complete.")
    print(f"Found {active_hosts} active hosts, {down_hosts} down, {error_hosts} errors.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fast network scanner using multithreading.")
    parser.add_argument("-n", "--network", help="Network to scan in CIDR format (e.g., 192.168.1.0/24)")
    parser.add_argument("-i", "--ips", nargs="+", help="Specific IPs to scan (e.g., 192.168.1.1 192.168.1.10)")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Number of threads (default: 50)")

    args = parser.parse_args()

    if args.network:
        network = ipaddress.ip_network(args.network, strict=False)
        ip_list = [str(ip) for ip in network.hosts()]  # Get all valid IPs in range
    elif args.ips:
        ip_list = args.ips  # Use manually provided IPs
    else:
        print("Error: You must provide a network range (-n) or specific IPs (-i).")
        exit(1)

    scan_ips(ip_list, args.threads)
