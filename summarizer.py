from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_message(message_text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Summarize WhatsApp chats clearly and briefly."},
            {"role": "user", "content": message_text}
        ]
    )
    return response.choices[0].message.content.strip()
