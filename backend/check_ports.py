import socket
import sys

def check_port(host, port, timeout=5):
    print(f"Checking {host}:{port}...", end='', flush=True)
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        print(" ✅ OPEN")
        return True
    except socket.timeout:
        print(" ❌ TIMEOUT")
    except ConnectionRefusedError:
        print(" ❌ REFUSED")
    except Exception as e:
        print(f" ❌ ERROR: {e}")
    return False

if __name__ == "__main__":
    print("--- Network Connectivity Test ---")
    
    # 1. Check Public IP (from .env)
    check_port("99.22.181.136", 5432)
    
    # 2. Check Localhost
    check_port("localhost", 5432)
    
    # 3. Check Localhost (IPv4 specific)
    check_port("127.0.0.1", 5432)
