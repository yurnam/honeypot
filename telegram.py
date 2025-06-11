import requests
import app_secrets
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
