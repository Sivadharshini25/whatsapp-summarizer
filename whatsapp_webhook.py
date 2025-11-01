import os
import json
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mywhatsapptoken")
WHATSAPP_MESSAGES_FILE = "whatsapp_messages.txt"

# -------------------------------------------------------
# 1️⃣ VERIFY WEBHOOK (GET request from Meta)
# -------------------------------------------------------
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("\n🟢 VERIFY REQUEST RECEIVED:")
    print(f"Mode: {mode}")
    print(f"Token received from Meta: {token}")
    print(f"Expected VERIFY_TOKEN: {VERIFY_TOKEN}")
    print(f"Challenge: {challenge}")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Verification success! Returning challenge...")
        return challenge, 200
    else:
        print("❌ Verification failed! Token mismatch.")
        return "Verification failed", 403


# -------------------------------------------------------
# 2️⃣ HANDLE INCOMING MESSAGES (POST request from Meta)
# -------------------------------------------------------
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("\n📨 Incoming webhook data:")
    print(json.dumps(data, indent=4))

    try:
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])

                    for msg in messages:
                        sender = msg.get("from")
                        text = msg.get("text", {}).get("body")

                        if sender and text:
                            print(f"📩 New message from {sender}: {text}")

                            # Save message to a file for later summarization
                            with open(WHATSAPP_MESSAGES_FILE, "a", encoding="utf-8") as f:
                                f.write(f"{sender}: {text}\n")
    except Exception as e:
        print(f"⚠️ Error processing message: {e}")

    return "EVENT_RECEIVED", 200


# -------------------------------------------------------
# 3️⃣ SIMPLE SUMMARY PAGE (for your website)
# -------------------------------------------------------
@app.route("/")
def home():
    try:
        with open(WHATSAPP_MESSAGES_FILE, "r", encoding="utf-8") as f:
            messages = f.readlines()
    except FileNotFoundError:
        messages = []

    summary = summarize_messages(messages)
    return f"""
    <html>
    <head><title>WhatsApp Message Summarizer</title></head>
    <body style="font-family: Arial; background-color: #f2f2f2; padding: 20px;">
        <h1>📱 WhatsApp Message Summary</h1>
        <p><b>Total Messages:</b> {len(messages)}</p>
        <h3>🗂 Recent Messages:</h3>
        <pre style="background:#fff; padding:10px; border-radius:8px;">{summary}</pre>
    </body>
    </html>
    """


# -------------------------------------------------------
# 4️⃣ BASIC SUMMARIZATION LOGIC (placeholder for OpenAI)
# -------------------------------------------------------
def summarize_messages(messages):
    if not messages:
        return "No messages received yet."

    last_msgs = messages[-5:]  # show last 5 messages for now
    summary = "\n".join([m.strip() for m in last_msgs])
    return summary


# -------------------------------------------------------
# 5️⃣ START FLASK APP
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(port=5000)


