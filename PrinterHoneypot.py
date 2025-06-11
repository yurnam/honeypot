# PrinterHoneypot.py

import socket
import threading
import os
from datetime import datetime
from telegram import send_telegram_message

class PrinterHoneypot:
    def __init__(self, host='0.0.0.0', port=9100):
        self.host = host
        self.port = port
        os.makedirs('print_jobs', exist_ok=True)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print(f"[PrinterHoneypot] Listening on port {self.port} (RAW printer)...")

        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

    def handle_client(self, client, addr):
        try:
            print(f"[PrinterHoneypot] Connection from {addr}")

            client.settimeout(5.0)

            # Read print job data
            full_data = b""
            try:
                while True:
                    chunk = client.recv(1024)
                    if not chunk:
                        break
                    full_data += chunk
                    if len(full_data) >= 10 * 1024 * 1024:  # 10 MB limit
                        break
            except socket.timeout:
                pass

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"print_jobs/print_{timestamp}_{addr[0]}.raw"

            with open(filename, "wb") as f:
                f.write(full_data)

            msg = f"*Printer honeypot hit!* 🐝\n"
            msg += f"`{datetime.utcnow().isoformat()}`\n"
            msg += f"*IP:* `{addr[0]}`\n"
            msg += f"*Print job size:* `{len(full_data)} bytes`\n"

            # For small print jobs, include first part of data
            if full_data:
                preview = full_data[:200].decode(errors='ignore')
                msg += f"*Preview:* ```\n{preview}\n```"

            send_telegram_message(msg)

            client.close()

        except Exception as e:
            print(f"[PrinterHoneypot] Exception: {e}")
            try:
                client.close()
            except:
                pass


if __name__ == '__main__':
    honeypot = PrinterHoneypot()
    honeypot.run()