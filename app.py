import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Get these from environment variables (set in Render dashboard)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ==== ការកំណត់ការឆ្លើយតប (Auto-reply settings) ====
# អ្នកអាចកែសារនេះបានតាមចង់
AUTO_REPLY_MESSAGE = (
    "សួស្តី! 🙏 សូមអភ័យទោស ខ្ញុំពុំទាន់អាចឆ្លើយបានភ្លាមៗទេ "
    "ព្រោះកំពុងរវល់។ ខ្ញុំនឹងឆ្លើយត្រឡប់ក្នុងពេលឆាប់ៗនេះ។ "
    "អរគុណសម្រាប់ការអត់ធ្មត់! 💕"
)

# ប្រសិនបើសារមានពាក្យទាំងនេះ ឆ្លើយតបខុសគ្នា (optional custom replies)
KEYWORD_REPLIES = {
    "តម្លៃ": "សូមរង់ចាំបន្តិច ខ្ញុំនឹងផ្ញើតម្លៃឱ្យអ្នកឆាប់ៗនេះ 🙏",
    "price": "Please wait, I'll send you the price shortly 🙏",
}


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload, timeout=10)


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # ជ្រើសរើសចម្លើយតាមពាក្យគន្លឹះ បើមាន
        reply = AUTO_REPLY_MESSAGE
        for keyword, custom_reply in KEYWORD_REPLIES.items():
            if keyword.lower() in text.lower():
                reply = custom_reply
                break

        send_message(chat_id, reply)

    return {"ok": True}


@app.route("/", methods=["GET"])
def home():
    return "Bot is running! ✅"


@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """
    ចូលទៅ URL នេះម្តងគត់ បន្ទាប់ពី deploy រួច ដើម្បីភ្ជាប់ bot ទៅ Render
    ឧទាហរណ៍: https://your-app.onrender.com/set_webhook
    """
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if not render_url:
        return {"error": "RENDER_EXTERNAL_URL not set"}, 400

    webhook_url = f"{render_url}/webhook"
    resp = requests.get(f"{TELEGRAM_API}/setWebhook", params={"url": webhook_url})
    return resp.json()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
