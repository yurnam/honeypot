# IMAP_Honeypot.py

import socket
import threading
import random
import time
import os
from datetime import datetime
from telegram import send_telegram_message

class IMAPHoneypot:
    def __init__(self, host='0.0.0.0', port=143):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print(f"[IMAPHoneypot] Listening on port {self.port} (IMAP)...")

        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

    def handle_client(self, client, addr):
        try:
            print(f"[IMAPHoneypot] Connection from {addr}")
            client.settimeout(10.0)

            # Greeting banner → random server
            server_name = random.choice([
                "Dovecot", "Courier", "Cyrus", "uw-imap", "Microsoft Exchange"
            ])
            random_id = os.urandom(4).hex()
            banner = f"* OK [{server_name} ready] <{random_id}>\r\n"
            client.sendall(banner.encode())

            logged_in = False
            message_count = random.randint(1, 20)

            while True:
                line = self.recv_line(client)
                if not line:
                    break

                parts = line.strip().split()
                if len(parts) < 2:
                    continue

                tag = parts[0]
                command = parts[1].upper()

                if command == "CAPABILITY":
                    caps = random.sample([
                        "IMAP4rev1", "LITERAL+", "SASL-IR", "UIDPLUS", "IDLE", "NAMESPACE", "XLIST", "STARTTLS", "AUTH=PLAIN"
                    ], random.randint(3, 6))
                    resp = f"* CAPABILITY {' '.join(caps)}\r\n{tag} OK CAPABILITY completed\r\n"
                    client.sendall(resp.encode())

                elif command == "NOOP":
                    client.sendall(f"{tag} OK NOOP completed\r\n".encode())

                elif command == "LOGOUT":
                    client.sendall(f"* BYE Logging out\r\n{tag} OK LOGOUT completed\r\n".encode())
                    break

                elif command == "LOGIN":
                    if len(parts) >= 4:
                        username = parts[2]
                        password = parts[3]
                        msg = f"*IMAP LOGIN!* 🐝\n"
                        msg += f"`{datetime.utcnow().isoformat()}`\n"
                        msg += f"*IP:* `{addr[0]}`\n"
                        msg += f"*Username:* `{username}`\n"
                        msg += f"*Password:* `{password}`"
                        send_telegram_message(msg)

                        logged_in = True
                        client.sendall(f"{tag} OK LOGIN completed\r\n".encode())
                    else:
                        client.sendall(f"{tag} BAD LOGIN failed\r\n".encode())

                elif command == "SELECT":
                    if not logged_in:
                        client.sendall(f"{tag} NO SELECT failed: Not logged in\r\n".encode())
                        continue
                    uidvalidity = random.randint(100000, 999999)
                    uidnext = random.randint(100, 999)
                    flags = "\\Answered \\Flagged \\Deleted \\Seen \\Draft"
                    resp = (
                        f"* {message_count} EXISTS\r\n"
                        f"* {random.randint(0, message_count)} RECENT\r\n"
                        f"* FLAGS ({flags})\r\n"
                        f"* OK [UIDVALIDITY {uidvalidity}] UIDs valid\r\n"
                        f"* OK [UIDNEXT {uidnext}] Predicted next UID\r\n"
                        f"{tag} OK [READ-WRITE] SELECT completed\r\n"
                    )
                    client.sendall(resp.encode())

                elif command == "FETCH":
                    if not logged_in:
                        client.sendall(f"{tag} NO FETCH failed: Not logged in\r\n".encode())
                        continue
                    fake_subject = os.urandom(6).hex()
                    fake_from = f"user{random.randint(1,999)}@example.com"
                    fake_date = datetime.utcnow().strftime("%d-%b-%Y %H:%M:%S +0000")
                    fake_body = os.urandom(32).hex()

                    resp = (
                        f"* 1 FETCH (FLAGS (\\Seen) RFC822.SIZE {len(fake_body)} "
                        f"BODY[] {{{len(fake_body)}}}\r\n{fake_body}\r\n)\r\n"
                        f"{tag} OK FETCH completed\r\n"
                    )
                    client.sendall(resp.encode())

                else:
                    # Unhandled command → generic OK
                    client.sendall(f"{tag} OK {command} completed\r\n".encode())

                # Random delay → look realistic
                time.sleep(random.uniform(0.05, 0.2))

            client.close()

        except Exception as e:
            print(f"[IMAPHoneypot] Exception: {e}")
            try:
                client.close()
            except:
                pass

    def recv_line(self, client):
        line = b""
        while not line.endswith(b"\r\n"):
            char = client.recv(1)
            if not char:
                break
            line += char
        return line.decode(errors='ignore')

if __name__ == '__main__':
    honeypot = IMAPHoneypot()
    honeypot.run()
