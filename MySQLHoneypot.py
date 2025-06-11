# MySQLHoneypot.py

import socket
import threading
from datetime import datetime
from telegram import send_telegram_message

# MySQL protocol constants (simplified)
MYSQL_HANDSHAKE = (
    b"\x0a"  # Protocol version
    b"5.5.5-10.1.69-MariaDB\x00"  # Server version (fake)
    b"\x0a\x00\x00\x00"  # Thread ID
    b"abcdefgh\x00"  # Salt part 1
    b"\xff\xf7\x08\x02\x00\x0f\xc0\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # Capabilities, charset, status
    b"ijklmnopqrstuvwx\x00"  # Salt part 2
    b"\x00"  # Filler
)

# Simplified fake OK packet
FAKE_OK_PACKET = b'\x07\x00\x00\x02\x00\x00\x00\x02\x00\x00'


class MySQLHoneypot:
    def __init__(self, host='0.0.0.0', port=3306):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print(f"[MySQLHoneypot] Listening on port {self.port}...")

        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

    def handle_client(self, client, addr):
        try:
            print(f"[MySQLHoneypot] Connection from {addr}")

            # Send handshake
            client.sendall(MYSQL_HANDSHAKE)

            client.settimeout(2.0)  # Wait up to 2 seconds for client data

            # Read client handshake response (username, capabilities)
            handshake_data = b""

            try:
                while True:
                    chunk = client.recv(1024)
                    if not chunk:
                        break
                    handshake_data += chunk
                    if len(handshake_data) >= 4096:
                        break
            except socket.timeout:
                pass

            # Parse username if possible
            username = "<unknown>"
            if len(handshake_data) >= 36:
                try:
                    username_start = handshake_data[36:].find(b'\x00')
                    username = handshake_data[36:36 + username_start].decode(errors='ignore')
                except Exception:
                    pass

            # Send initial connection Telegram message
            msg = f"*MySQL connection!* 🐝\n"
            msg += f"`{datetime.utcnow().isoformat()}`\n"
            msg += f"*IP:* `{addr[0]}`\n"
            msg += f"*Username:* `{username}`\n"

            if handshake_data:
                msg += f"*Raw handshake packet:* ```\n{handshake_data.hex()}\n```"
            else:
                msg += "*No handshake data received (client disconnected early)*"

            send_telegram_message(msg)

            # Send fake OK packet → makes bots send queries
            client.sendall(FAKE_OK_PACKET)

            # Read possible queries
            client.settimeout(5.0)  # Wait up to 5 seconds for queries

            while True:
                try:
                    query_data = client.recv(1024)
                    if not query_data:
                        break

                    # MySQL COM_QUERY packet starts with 0x03
                    if query_data[4] == 0x03:
                        query = query_data[5:].decode(errors='ignore')

                        query_msg = f"*MySQL query received!* 🐝\n"
                        query_msg += f"`{datetime.utcnow().isoformat()}`\n"
                        query_msg += f"*IP:* `{addr[0]}`\n"
                        query_msg += f"*Username:* `{username}`\n"
                        query_msg += f"*Query:* ```\n{query}\n```"

                        send_telegram_message(query_msg)

                except socket.timeout:
                    break  # No more data → end of session

            client.close()

        except Exception as e:
            print(f"[MySQLHoneypot] Exception: {e}")
            try:
                client.close()
            except:
                pass


if __name__ == '__main__':
    honeypot = MySQLHoneypot()
    honeypot.run()
