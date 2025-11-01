from flask import Flask, request, jsonify, render_template
import os
import openai
from datetime import datetime

app = Flask(__name__)

# ===============================
# CONFIGURATION
# ===============================
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mywhatsapptoken")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Store messages in memory for now
messages = []

# ===============================
# ROUTES
# ===============================

@app.route('/')
def home():
    """Display summarized WhatsApp messages."""
    return render_template("index.html", messages=messages)

@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    if request.method == 'GET':
        # Meta verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        print("🟢 VERIFY REQUEST RECEIVED:")
        print(f"Mode: {mode}")
        print(f"Token received from Meta: {token}")
        print(f"Expected VERIFY_TOKEN: {VERIFY_TOKEN}")
        print(f"Challenge: {challenge}")

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("✅ Verification success! Returning challenge...")
            return challenge, 200
        else:
            print("❌ Verification failed!")
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

                print(f"\n📩 New message from {sender}: {text}")

                # Generate summary using OpenAI
                summary = summarize_message(text)

                # Store summary in memory
                messages.append({
                    "sender": sender,
                    "text": text,
                    "summary": summary,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

        except Exception as e:
            print("⚠️ Error processing message:", e)

        return jsonify({"status": "received"}), 200


# ===============================
# HELPER FUNCTIONS
# ===============================

def summarize_message(text):
    """Use OpenAI API to summarize a WhatsApp message."""
    try:
        prompt = f"Summarize this WhatsApp message briefly:\n\n{text}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("⚠️ OpenAI error:", e)
        return "(Summary unavailable)"


# ===============================
# MAIN ENTRY
# ===============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


