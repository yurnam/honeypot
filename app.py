from flask import Flask, request
from random import randint
from os import urandom
import requests
import app_secrets
from datetime import datetime
import returns
from telegram import send_telegram_message
from FTPHoneypot import FTPHoneypot
import threading
import ssh_honeypot
from SMTPHoneypot import SMTPHoneypot
from MySQLHoneypot import MySQLHoneypot
from PrinterHoneypot import PrinterHoneypot
from SIPHoneypot import SIPHoneypot
from RDPHoneypot import RDPHoneypot
from TelnetHoneypot import TelnetHoneypot
from VNC_Crasher_Honeypot import VNCCrasherHoneypot
from MQTT_Honeypot import MQTTHoneypot
app = Flask(__name__)


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


@app.after_request
def add_server_header(response):
    response.headers['Server'] = 'Apache/2.4.18 (Ubuntu)'
    return response


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


import threading


def run_http():
    app.run(host='0.0.0.0', port=80)


def run_https():
    context = ('certs/cert.pem', 'certs/key.pem')
    app.run(host='0.0.0.0', port=443, ssl_context=context)


if __name__ == '__main__':
    # Start FTP honeypot in background thread
    ftp_honeypot = FTPHoneypot(port=21)
    ftp_thread = threading.Thread(target=ftp_honeypot.run, daemon=True)
    ftp_thread.start()

    # Start SMTP honeypot in background thread
    smtp_honeypot = SMTPHoneypot(port=25)
    smtp_thread = threading.Thread(target=smtp_honeypot.run, daemon=True)
    smtp_thread.start()

    # Start SSH honeypot in background thread
    ssh_thread = threading.Thread(target=ssh_honeypot.run_ssh_honeypot, daemon=True)
    ssh_thread.start()

    # Start HTTP honeypot in background thread
    http_thread = threading.Thread(target=run_http, daemon=True)
    http_thread.start()

    # Start MySQL honeypot in background thread
    mysql_honeypot = MySQLHoneypot(port=3306)
    mysql_thread = threading.Thread(target=mysql_honeypot.run, daemon=True)
    mysql_thread.start()

    # start the printer honeypot in background thread
    printer_honeypot = PrinterHoneypot(port=9100)
    printer_thread = threading.Thread(target=printer_honeypot.run, daemon=True)
    printer_thread.start()
    # start the SIP honeypot in background thread

    sip_honeypot = SIPHoneypot(port=5060)
    sip_thread = threading.Thread(target=sip_honeypot.run, daemon=True)
    sip_thread.start()

    # start the RDP honeypot in background thread
    rdp_honeypot = RDPHoneypot(port=3389)
    rdp_thread = threading.Thread(target=rdp_honeypot.run, daemon=True)
    rdp_thread.start()

    # start the telnet honeypot in background thread
    telnet_honeypot = TelnetHoneypot(port=23)
    telnet_thread = threading.Thread(target=telnet_honeypot.run, daemon=True)
    telnet_thread.start()
    # start the VNC crasher honeypot in background thread
    vnc_crasher_honeypot = VNCCrasherHoneypot(port=5900)
    vnc_crasher_thread = threading.Thread(target=vnc_crasher_honeypot.run, daemon=True)
    vnc_crasher_thread.start()

    # start the MQTT honeypot in background thread
    mqtt_honeypot = MQTTHoneypot(port=1883)
    mqtt_thread = threading.Thread(target=mqtt_honeypot.run, daemon=True)
    mqtt_thread.start()



    # Start HTTPS honeypot → run in main thread
    run_https()
