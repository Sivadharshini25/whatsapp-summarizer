from flask import Flask, render_template, request, jsonify
import requests
import openai

app = Flask(__name__)

# ---- CONFIG ----
# Get your tokens from environment variables or hardcode temporarily for testing.
# ⚠️ Never hardcode secrets in production.
WHATSAPP_TOKEN = "YOUR_WHATSAPP_CLOUD_API_TOKEN"
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID"  # from Meta App Dashboard
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

openai.api_key = OPENAI_API_KEY


# ---- ROUTES ----
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/connect', methods=['POST'])
def connect_whatsapp():
    """Simulate WhatsApp Business connection."""
    data = request.json
    number = data.get("number")

    if not number:
        return jsonify({"error": "No number provided"}), 400

    # Here, you could verify the number via the Cloud API
    # For demo: assume it’s successfully linked
    return jsonify({"message": f"Connected successfully to {number}!"})


@app.route('/summarize', methods=['POST'])
def summarize_messages():
    """Fetch messages from WhatsApp and summarize them."""
    try:
        # Step 1: Fetch messages from WhatsApp Cloud API
        url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        # You can replace with actual message fetch or mock sample:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch messages from WhatsApp."}), 500

        # For demo, we’ll mock messages
        chats = [
            "Hey, can we reschedule the meeting to tomorrow?",
            "Your package has been shipped. Tracking ID: 12345.",
            "Don’t forget to submit the report by EOD."
        ]

        # Step 2: Summarize using OpenAI
        prompt = "Summarize these WhatsApp messages in a short, clear paragraph:\n\n" + "\n".join(chats)

        summary_response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

        summary = summary_response["choices"][0]["message"]["content"]

        return jsonify({"summary": summary})

    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while summarizing."}), 500


if __name__ == '__main__':
    app.run(debug=True)

