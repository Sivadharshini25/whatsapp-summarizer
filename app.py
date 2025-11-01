from flask import Flask, request, jsonify, render_template
import os
from datetime import datetime
from transformers import pipeline

app = Flask(__name__)

# -----------------------------
# CONFIG
# -----------------------------
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mywhatsapptoken")

# Temporary in-memory data
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
        # Meta verification step
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        print("🟢 VERIFY REQUEST RECEIVED:")
        print(f"Mode: {mode}")
        print(f"Token received: {token}")
        print(f"Expected: {VERIFY_TOKEN}")

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Verification success! Returning challenge...")
            return challenge, 200
        else:
            print("❌ Verification failed.")
            return "Forbidden", 403

    elif request.method == 'POST':
        # Handle incoming WhatsApp message
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
# FETCH MESSAGES ENDPOINT
# -----------------------------
@app.route("/get_messages")
def get_messages():
    return jsonify({"messages": messages})

# -----------------------------
# SUMMARIZATION ENDPOINT
# -----------------------------
@app.route('/summarize', methods=['POST'])
def summarize_all():
    if not messages:
        return jsonify({"error": "No messages received yet."}), 400

    all_text = "\n".join([m["text"] for m in messages])
    try:
        summary = summarize_text(all_text)
        print("🧠 Summary generated successfully.")
        return jsonify({"summary": summary})
    except Exception as e:
        print("⚠️ Summarization error:", e)
        return jsonify({"error": "Failed to generate summary."}), 500

# -----------------------------
# SUMMARIZER FUNCTION
# -----------------------------
print("⚙️ Loading summarization model...")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text):
    text = text.strip()
    if len(text) < 20:
        return "Not enough content to summarize."

    try:
        summary = summarizer(text, max_length=120, min_length=25, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print("⚠️ Summarization error:", e)
        return "Failed to generate summary."

# -----------------------------
# MAIN ENTRY
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



