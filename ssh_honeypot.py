# ssh_honeypot.py

import socket
import paramiko
import threading
import app_secrets
import requests
from datetime import datetime

# Function to send Telegram message
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{app_secrets.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": app_secrets.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

# SSH server implementation
class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        super().__init__()
        self.client_ip = client_ip

    def check_auth_password(self, username, password):
        msg = f"*SSH login attempt!* 🐝\n"
        msg += f"`{datetime.utcnow().isoformat()}`\n"
        msg += f"*IP:* `{self.client_ip}`\n"
        msg += f"*Username:* `{username}`\n"
        msg += f"*Password:* `{password}`\n"

        send_telegram_message(msg)
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        return True

def handle_client(client, addr):
    transport = paramiko.Transport(client)
    transport.add_server_key(paramiko.RSAKey.generate(2048))
    server = FakeSSHServer(addr[0])

    try:
        transport.start_server(server=server)
        chan = transport.accept(20)
        if chan is None:
            return

        chan.send(b"Welcome to fake SSH!\n")
        while True:
            chan.send(b"$ ")
            command = ""
            while not command.endswith("\n"):
                command += chan.recv(1024).decode("utf-8", errors="ignore")
            command = command.strip()

            msg = f"*SSH command!* 🐝\n"
            msg += f"`{datetime.utcnow().isoformat()}`\n"
            msg += f"*IP:* `{addr[0]}`\n"
            msg += f"*Command:* `{command}`\n"

            send_telegram_message(msg)
            chan.send(b"Command not found\n")
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        transport.close()

def run_ssh_honeypot(port=2222):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', port))
    sock.listen(100)
    print(f"[SSH Honeypot] Listening on port {port}...")

    while True:
        client, addr = sock.accept()
        print(f"[SSH Honeypot] Connection from {addr}")
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()
