import socket
import json
import time

server_host = '127.0.0.1'
server_port = 9999

def start_backend():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_host, server_port))
    server.listen(1)
    print("Waiting on Java to connect...")
    
    client_socket, address = server.accept()
    print(f"Connected! {address}")
    
    try:
        raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        print("Raw socket successfully created!")
    except PermissionError:
        print("\n[!] PERMISSION ERROR: Raw packet sniffing requires admin privileges.")
        print("Please run this script using: sudo python3 sniffer.py\n")
        return

    prev_time = time.time()
    bytes_in_window = 0

    print("[+] Starting packet capture loop...")

    while True:
        try:
            raw_data, _ = raw_socket.recvfrom(65535)

            packet_len = len(raw_data)
            bytes_in_window += packet_len

            curr_time = time.time()
            dt = curr_time - prev_time

            rate_kbps = 0.0
            spike_detected = False
            if dt >= 1.0:
                rate_kbps = (bytes_in_window / 1024) / dt
                if rate_kbps > 500:
                    spike_detected = True

                bytes_in_window = 0
                prev_time = curr_time

            telemetry = {
                "timestamp": round(curr_time, 2),
                "bytes": packet_len,
                "rate_kbps": round(rate_kbps, 2),
                "spike": spike_detected
            }

            json_line = json.dumps(telemetry) + "\n"
            client_socket.send(json_line.encode("utf-8"))

        except (ConnectionResetError, BrokenPipeError):
            print("[-] Java Frontend disconnected. Waiting for reconnect...")
            client_socket, address = server.accept()

if __name__ == "__main__":
    start_backend()