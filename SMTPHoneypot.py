# SMTPHoneypot.py

import asyncio
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import AsyncMessage
from telegram import send_telegram_message
from datetime import datetime
import email

class SMTPHandler(AsyncMessage):
    async def handle_message(self, message):
        # Parse email message
        from_addr = message['From']
        to_addrs = message.get_all('To', [])
        subject = message.get('Subject', '')
        body = message.get_payload()

        # Build Telegram message
        msg = f"*SMTP email attempt!* 🐝\n"
        msg += f"`{datetime.utcnow().isoformat()}`\n"
        msg += f"*From:* `{from_addr}`\n"
        msg += f"*To:* `{to_addrs}`\n"
        msg += f"*Subject:* `{subject}`\n"
        msg += f"*Body:* ```\n{body}\n```\n"

        send_telegram_message(msg)

class SMTPHoneypot:
    def __init__(self, host='0.0.0.0', port=25):
        self.host = host
        self.port = port

    def run(self):
        handler = SMTPHandler()
        controller = Controller(handler, hostname=self.host, port=self.port)
        print(f"[SMTPHoneypot] Listening on port {self.port}...")
        controller.start()

        # Keep running
        try:
            while True:
                asyncio.sleep(1)
        except KeyboardInterrupt:
            print("[SMTPHoneypot] Stopping...")
            controller.stop()
