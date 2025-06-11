# RDPHoneypot.py

import socket
import threading
from datetime import datetime
from telegram import send_telegram_message

# X.224 Connection Confirm + RDP Negotiation Response
# Realistic → makes many bots proceed after this
FAKE_RDP_RESPONSE = bytes.fromhex(
    # TPKT Header (RFC 1006)
    "0300001b"  # Length 27 bytes
    # X.224 Data
    "0e00"      # X.224 length indicator
    "d000"      # X.224 Connection Confirm (0xd0)
    "0000000000000000"
    "03000008"  # RDP Negotiation Response header
    "0200"      # Type: Response (0x02)
    "0000"      # Flags: none
    "0800"      # Length of the negotiation data
    "00000000"  # Selected Protocol (0x00000000) → Standard RDP Security
)

class RDPHoneypot:
    def __init__(self, host='0.0.0.0', port=3389):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print(f"[RDPHoneypot] Listening on port {self.port} (RDP)...")

        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

    def handle_client(self, client, addr):
        try:
            print(f"[RDPHoneypot] Connection from {addr}")

            # Send fake RDP response
            client.sendall(FAKE_RDP_RESPONSE)

            client.settimeout(10.0)  # Give bots time to send data

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

            msg = f"*RDP connection!* 🐝\n"
            msg += f"`{datetime.utcnow().isoformat()}`\n"
            msg += f"*IP:* `{addr[0]}`\n"
            msg += f"*Port:* `{addr[1]}`\n"
            msg += f"*Data received:* `{len(full_data)} bytes`\n"

            if full_data:
                preview = full_data[:200].hex()
                msg += f"*Data preview (hex):* ```\n{preview}\n```"
            else:
                msg += "*No data received (client disconnected early)*"

            send_telegram_message(msg)

            client.close()

        except Exception as e:
            print(f"[RDPHoneypot] Exception: {e}")
            try:
                client.close()
            except:
                pass
if __name__ == '__main__':
    honeypot = RDPHoneypot()
    honeypot.run()