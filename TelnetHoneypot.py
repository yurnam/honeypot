# TelnetHoneypot.py

import socket
import threading
from datetime import datetime
from telegram import send_telegram_message

class TelnetHoneypot:
    def __init__(self, host='0.0.0.0', port=23):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print(f"[TelnetHoneypot] Listening on port {self.port} (Telnet)...")

        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

    def handle_client(self, client, addr):
        try:
            print(f"[TelnetHoneypot] Connection from {addr}")

            client.settimeout(60.0)  # Give bot time to send data

            # Send login prompt
            client.sendall(b"\nlogin: ")
            username = self.read_line(client).strip()

            # Send password prompt
            client.sendall(b"Password: ")
            password = self.read_line(client).strip()

            # Log credentials
            msg = f"*Telnet login attempt!* 🐝\n"
            msg += f"`{datetime.utcnow().isoformat()}`\n"
            msg += f"*IP:* `{addr[0]}`\n"
            msg += f"*Username:* `{username}`\n"
            msg += f"*Password:* `{password}`\n"

            send_telegram_message(msg)

            # Optional: simulate fake shell to waste bot time
            client.sendall(b"\nWelcome to Linux 4.14.0 (ttyS0)\n\n$ ")

            session_data = b""
            try:
                while True:
                    chunk = client.recv(1024)
                    if not chunk:
                        break
                    session_data += chunk
                    if len(session_data) >= 10 * 1024 * 1024:
                        break
                    # Simulate shell prompt again
                    client.sendall(b"$ ")
            except socket.timeout:
                pass

            # Log session data
            if session_data:
                msg2 = f"*Telnet session data!* 🐝\n"
                msg2 += f"`{datetime.utcnow().isoformat()}`\n"
                msg2 += f"*IP:* `{addr[0]}`\n"
                msg2 += f"*Session data:* ```\n{session_data.decode(errors='ignore')}\n```"

                send_telegram_message(msg2)

            client.close()

        except Exception as e:
            print(f"[TelnetHoneypot] Exception: {e}")
            try:
                client.close()
            except:
                pass

    def read_line(self, client):
        line = b""
        while True:
            try:
                char = client.recv(1)
                if not char or char == b"\n" or char == b"\r":
                    break
                line += char
            except socket.timeout:
                break
        return line.decode(errors="ignore")

