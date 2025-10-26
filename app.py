from flask import Flask, request, jsonify
import openai
from twilio.rest import Client

app = Flask(__name__)

# -------------------------
# 🔐 Configuration (fill these in)
# -------------------------
OPENAI_API_KEY = "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"
TWILIO_SID = "ACe72f24d985b7f5b464f8d3d6550dedfd"
TWILIO_AUTH = "47cbf3961494edf4b009be38a0a42d99"
TWILIO_WHATSAPP = "whatsapp:+14155238886"   # ✅ Twilio sandbox number
BROTHER_WHATSAPP = "whatsapp:9792714619" # ✅ Your brother's WhatsApp number


openai.api_key = OPENAI_API_KEY


# -------------------------
# 📬 GitHub Webhook Endpoint
# -------------------------
@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    data = request.json

    # Extract repo and pusher info
    repo_name = data['repository']['full_name']
    pusher = data['pusher']['name']
    commits = data.get('commits', [])

    changed_files = []
    commit_messages = []

    # Gather all commit details
    for commit in commits:
        commit_messages.append(commit['message'])
        changed_files.extend(commit.get('modified', []))

    # 🧠 Detect if your daily tracker file is updated
    is_daily_update = any(
        "daily" in file.lower() or "progress" in file.lower()
        for file in changed_files
    )

    # -------------------------
    # 🧠 Create a smart AI summary
    # -------------------------
    if is_daily_update:
        prompt = f"""
        Summarize these GitHub commits as if summarizing a daily progress sheet update.
        Example style: 'Sabhya completed ReactJS Interview prep and started AWS training.'
        Commits: {commit_messages}
        Changed files: {changed_files}
        """
    else:
        prompt = f"""
        Summarize these GitHub commits in one line:
        Commits: {commit_messages}
        Changed files: {changed_files}
        """

    try:
        ai_summary = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content.strip()
    except Exception as e:
        ai_summary = f"Could not generate summary: {e}"

    # -------------------------
    # 💬 Send WhatsApp Message via Twilio
    # -------------------------
    msg_body = f"""
📢 GitHub Update Alert!

📂 Repo: {repo_name}
👤 By: {pusher}
🗂️ Files Changed: {', '.join(changed_files) if changed_files else 'No files listed'}
🧠 Summary: {ai_summary}
    """

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        message = client.messages.create(
            from_=TWILIO_WHATSAPP,
            to=BROTHER_WHATSAPP,
            body=msg_body
        )
        print("✅ WhatsApp notification sent:", message.sid)
    except Exception as e:
        print("❌ Error sending WhatsApp message:", e)

    return jsonify({"status": "ok"}), 200


# -------------------------
# 🏠 Home Route (for testing)
# -------------------------
@app.route('/')
def home():
    return "🚀 GitHub AI WhatsApp Notifier is running!"


# -------------------------
# 🏁 Run the App
# -------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

