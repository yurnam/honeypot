from flask import Flask, request
from random import randint
from os import urandom
import requests
import app_secrets
from datetime import datetime
import returns
app = Flask(__name__)


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


def log_and_send(req):
    timestamp = datetime.utcnow().isoformat()

    # Raw body
    body = ""
    try:
        body = req.get_data(as_text=True)
    except Exception as e:
        body = f"<could not decode> ({e})"

    # Query params
    query_params = req.args.to_dict(flat=False)

    # Form data (POST forms)
    form_data = req.form.to_dict(flat=False)

    # JSON (if any)
    json_data = {}
    try:
        json_data = req.get_json(force=False, silent=True) or {}
    except Exception:
        json_data = {}

    # Build message
    msg = f"*Honeypot hit!* 🐝\n"
    msg += f"`{timestamp}`\n"
    msg += f"*IP:* `{req.remote_addr}`\n"
    msg += f"*Method:* `{req.method}`\n"
    msg += f"*Path:* `{req.path}`\n"
    msg += f"*Query params:* ```\n{query_params}\n```\n"
    msg += f"*Form data:* ```\n{form_data}\n```\n"
    msg += f"*JSON body:* ```\n{json_data}\n```\n"
    msg += f"*Headers:* ```\n"
    for header, value in req.headers.items():
        msg += f"{header}: {value}\n"
    msg += "```\n"
    if body.strip():
        msg += f"*Raw body:* ```\n{body}\n```\n"

    # Send Telegram
    send_telegram_message(msg)



@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'PROST'])
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD', 'PROST'])
def catch_all(path):
    log_and_send(request)

    randomdata = urandom(randint(120, 1024))
    randomdata = randomdata.decode('utf-8', errors='ignore')

    return randomdata, 200

# im a teapot joke
@app.route('/brew', methods=['GET'])
def teapot():
    log_and_send(request)
    return "I'm a teapot", 418




if __name__ == '__main__':
    import threading
    import ssh_honeypot

    # Start SSH honeypot in background thread
    ssh_thread = threading.Thread(target=ssh_honeypot.run_ssh_honeypot, daemon=True)
    ssh_thread.start()

    # Start HTTP honeypot (main thread)
    app.run(host='0.0.0.0', port=80)
