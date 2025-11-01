from flask import Flask, request, jsonify, render_template
import os
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mywhatsapptoken")
messages = []


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route('/')
def home():
    return render_template("index.html")


# -----------------------------
# WEBHOOK HANDLER (META)
# -----------------------------
@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Verification success! Returning challenge...")
            return challenge, 200
        else:
            print("❌ Verification failed.")
            return "Forbidden", 403

    elif request.method == 'POST':
        data = request.get_json()
        print("\n📨 Incoming webhook data:")
        print(data)

        try:
            entry = data["entry"][0]["changes"][0]["value"]
            if "messages" in entry:
                msg = entry["messages"][0]
                sender = msg["from"]
                text = msg["text"]["body"]

                print(f"\n📩 Message from {sender}: {text}")

                messages.append({
                    "sender": sender,
                    "text": text,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        except Exception as e:
            print("⚠️ Error processing message:", e)

        return jsonify({"status": "received"}), 200


# -----------------------------
# MESSAGES ENDPOINT
# -----------------------------
@app.route('/get_messages')
def get_messages():
    return jsonify({"messages": messages})


# -----------------------------
# MAIN ENTRY
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




