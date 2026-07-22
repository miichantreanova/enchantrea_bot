import os
import logging
from flask import Flask, request
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ទាញ Token ពី Environment Variable (កំណត់នៅលើ Render, កុំសរសេរដាក់ត្រង់នេះ)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{8831823954:AAHkLLISgDzVOLqfRGieSZ7gm6E2Z-6Ajqs}"

# Secret token ដើម្បីការពារ webhook ពីអ្នកក្រៅ (ស្រេចចិត្តតែណែនាំឱ្យប្រើ)
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")


def send_message(chat_id, text):
    """ផ្ញើសារត្រឡប់ទៅអ្នកប្រើ"""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to send message: {e}")


def build_reply(text: str) -> str:
    """
    ត្រង់នេះជាកន្លែងកំណត់ថា bot ត្រូវឆ្លើយអ្វី។
    ឥឡូវនេះជាឧទាហរណ៍សាមញ្ញ (auto-reply) — អ្នកអាចកែតម្រូវតាមចង់បាន
    ឬតភ្ជាប់ទៅ Claude API សម្រាប់ការឆ្លើយឆ្លាតជាងនេះនាពេលក្រោយ។
    """
    text_lower = text.lower().strip()

    if text_lower in ("/start", "start"):
        return "សួស្តី! ខ្ញុំជាបូតជំនួយរបស់ En ChanTrea 🐻\nសរសេរអ្វីមក ខ្ញុំនឹងឆ្លើយឱ្យ។"
    if text_lower in ("/help", "help"):
        return "ខ្ញុំអាចជួយឆ្លើយសារឱ្យអ្នកម្ចាស់ខណៈគាត់មិនទាន់មានពេលឆ្លើយ។"
    if "តម្លៃ" in text or "price" in text_lower:
        return "សូមអភ័យទោស ខ្ញុំជាបូតឆ្លើយសារស្វ័យប្រវត្តិ។ ម្ចាស់នឹងឆ្លើយអ្នកវិញឆាប់ៗនេះ 🙏"

    return "ទទួលបានសាររបស់អ្នកហើយ! ម្ចាស់នឹងឆ្លើយត្រឡប់មកវិញឆាប់ៗនេះ 😊"


@app.route("/", methods=["GET"])
def index():
    return "Bot is running.", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    # ត្រួតពិនិត្យ secret token បើមាន (ការពារសុវត្ថិភាព)
    if WEBHOOK_SECRET:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header_secret != WEBHOOK_SECRET:
            return "forbidden", 403

    update = request.get_json(force=True, silent=True) or {}
    logger.info(f"Update received: {update}")

    message = update.get("message") or update.get("edited_message")
    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        if text:
            reply = build_reply(text)
            send_message(chat_id, reply)

    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
