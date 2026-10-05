import socket
import sys
from colorama import Fore, Style

KNOWN_SERVICES = {
    21: "ftp",
    22: "ssh",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    143: "imap",
    443: "https",
    993: "imaps",
    995: "pop3s",
    3306: "mysql",
    5432: "postgresql",
    6379: "redis",
    8080: "http-alt",
    8443: "https-alt",
}


def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip, port))
    sock.close()
    return result == 0


if len(sys.argv) != 3:
    print("Использование: python3 scanp.py <IP> <порты>")
    print("Пример: python3 scanp.py 127.0.0.1 22,80,443")
    print("Диапазон: python3 scanp.py 127.0.0.1 1-100")
    print("Микс: python3 scanp.py 127.0.0.1 22,80,8000-8100")
    sys.exit(1)

ip = sys.argv[1]
ports_str = sys.argv[2]
ports = []
for part in ports_str.split(","):
    if "-" in part:
        start,end = part.split("-")
        ports.extend(range(int(start), int(end) + 1))
    else:
        ports.append(int(part))

print(f"\n scan {ip}...\n")
print(f"{'PORT':<10} {'STATE':<10} {'SERVICE':<10}")
print("-" * 30)

for port in ports:
    if check_port(ip, port):
        state = Fore.GREEN + "open" + Style.RESET_ALL
    else:
        state = Fore.RED + "closed" + Style.RESET_ALL

    service = KNOWN_SERVICES.get(port, "unknown")
    print(f"{port:<10} {state:<10} {service:<10}")

print("\nscan end")