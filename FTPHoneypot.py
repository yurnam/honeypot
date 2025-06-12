# FTPHoneypot.py

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from datetime import datetime
from telegram import send_telegram_message


class HoneypotAuthorizer(DummyAuthorizer):
    def validate_authentication(self, username, password, handler):
        # Log login attempt
        msg = f"*FTP login attempt!* 🐝\n"
        msg += f"`{datetime.utcnow().isoformat()}`\n"
        msg += f"*IP:* `{handler.remote_ip}`\n"
        msg += f"*Username:* `{username}`\n"
        msg += f"*Password:* `{password}`\n"
        #send_telegram_message(msg)

        # Always accept login → honeypot behavior
        return True


class HoneypotFTPHandler(FTPHandler):
    def on_connect(self):
        pass  # optional

    def on_disconnect(self):
        pass  # optional

    def on_login(self, username):
        pass  # already logged in Authorizer

    def on_file_received(self, file):
        msg = f"*FTP file upload!* 🐝\n"
        msg += f"`{datetime.utcnow().isoformat()}`\n"
        msg += f"*IP:* `{self.remote_ip}`\n"
        msg += f"*Uploaded file:* `{file}`\n"
        send_telegram_message(msg)

    def on_incomplete_file_received(self, file):
        msg = f"*FTP incomplete upload!* 🐝\n"
        msg += f"`{datetime.utcnow().isoformat()}`\n"
        msg += f"*IP:* `{self.remote_ip}`\n"
        msg += f"*File:* `{file}`\n"
        send_telegram_message(msg)

    def on_file_sent(self, file):
        msg = f"*FTP file download!* 🐝\n"
        msg += f"`{datetime.utcnow().isoformat()}`\n"
        msg += f"*IP:* `{self.remote_ip}`\n"
        msg += f"*Downloaded file:* `{file}`\n"
        send_telegram_message(msg)


class FTPHoneypot:
    def __init__(self, host='0.0.0.0', port=21):
        self.host = host
        self.port = port

    def run(self):
        authorizer = HoneypotAuthorizer()
        # Add fake user → no real permission needed
        authorizer.add_user('user', '12345', '.', perm='elradfmw')  # Full perms → for triggering events

        handler = HoneypotFTPHandler
        handler.authorizer = authorizer

        server = FTPServer((self.host, self.port), handler)
        print(f"[FTPHoneypot] Listening on port {self.port}...")
        server.serve_forever()
