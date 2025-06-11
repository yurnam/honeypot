# SIPHoneypot.py

import socket
import threading
from datetime import datetime
from telegram import send_telegram_message


class SIPHoneypot:
    def __init__(self, host='0.0.0.0', port=5060):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        print(f"[SIPHoneypot] Listening on UDP port {self.port} (SIP)...")

        while True:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=self.handle_packet, args=(data, addr, sock), daemon=True).start()

    def handle_packet(self, data, addr, sock):
        try:
            sip_text = data.decode(errors='ignore')
            print(f"[SIPHoneypot] Packet from {addr}")

            # Basic SIP message type
            lines = sip_text.split('\r\n')
            first_line = lines[0] if lines else ""
            msg_type = first_line.split(' ')[0]

            # Extract useful headers
            from_header = next((line for line in lines if line.lower().startswith('from:')), "<none>")
            to_header = next((line for line in lines if line.lower().startswith('to:')), "<none>")
            call_id = next((line for line in lines if line.lower().startswith('call-id:')), "<none>")
            user_agent = next((line for line in lines if line.lower().startswith('user-agent:')), "<none>")

            msg = f"*SIP packet received!* 🐝\n"
            msg += f"`{datetime.utcnow().isoformat()}`\n"
            msg += f"*IP:* `{addr[0]}:{addr[1]}`\n"
            msg += f"*Type:* `{msg_type}`\n"
            msg += f"*From:* `{from_header}`\n"
            msg += f"*To:* `{to_header}`\n"
            msg += f"*Call-ID:* `{call_id}`\n"
            msg += f"*User-Agent:* `{user_agent}`\n"
            msg += f"*Payload:* ```\n{sip_text[:500]}\n```"

           # send_telegram_message(msg)

            if msg_type == "OPTIONS":
                # Fake 200 OK for OPTIONS
                response = (
                    f"SIP/2.0 200 OK\r\n"
                    f"Via: {self.get_via(lines)}\r\n"
                    f"From: {from_header}\r\n"
                    f"To: {to_header}\r\n"
                    f"Call-ID: {call_id}\r\n"
                    f"CSeq: 1 OPTIONS\r\n"
                    f"Content-Length: 0\r\n\r\n"
                )
                sock.sendto(response.encode(), addr)


            elif msg_type == "REGISTER":

                # FAKE SUCCESS → 200 OK → no honeypot markers

                response = (
                    f"SIP/2.0 200 OK\r\n"
                    f"Via: {self.get_via(lines)}\r\n"
                    f"From: {from_header}\r\n"
                    f"To: {to_header};tag=3d19b7f\r\n"  # Random looking tag
                    f"Call-ID: {call_id}\r\n"
                    f"CSeq: 1 REGISTER\r\n"
                    f"Contact: <sip:{addr[0]}:{self.port}>\r\n"
                    f"Content-Length: 0\r\n\r\n"

                )

                sock.sendto(response.encode(), addr)


            elif msg_type == "INVITE":

                # FAKE 200 OK → simulate successful call setup

                response = (

                    f"SIP/2.0 200 OK\r\n"
                    f"Via: {self.get_via(lines)}\r\n"
                    f"From: {from_header}\r\n"
                    f"To: {to_header};tag=4f9c4f6b\r\n"  # Random tag
                    f"Call-ID: {call_id}\r\n"
                    f"CSeq: 1 INVITE\r\n"
                    f"Contact: <sip:{addr[0]}:{self.port}>\r\n"
                    f"Content-Type: application/sdp\r\n"
                    f"Content-Length: 0\r\n\r\n"

                )

                sock.sendto(response.encode(), addr)


        except Exception as e:
            print(f"[SIPHoneypot] Exception: {e}")

    def get_via(self, lines):
        return next((line.split(':', 1)[1].strip() for line in lines if line.lower().startswith('via:')), "SIPHoneypot")


if __name__ == '__main__':
    honeypot = SIPHoneypot()
    honeypot.run()  # Default SIP port
