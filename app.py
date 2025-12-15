from flask import Flask, request, render_template, redirect, url_for
import os
import services
from database import (
    init_db,
    save_message,
    get_recent_chats,
    get_chat
)

app = Flask(__name__)
init_db()

TOKEN = os.getenv("TOKEN")


# =====================
# DASHBOARD
# =====================

@app.route("/")
def dashboard():
    chats = get_recent_chats()
    return render_template("index.html", chats=chats)


@app.route("/chat/<wa_id>")
def chat_view(wa_id):
    messages = get_chat(wa_id)
    return render_template("chat.html", wa_id=wa_id, messages=messages)


@app.route("/send_message/<wa_id>", methods=["POST"])
def send_message_panel(wa_id):
    text = request.form.get("text")
    data = services.text_Message(wa_id, text)
    services.enviar_Mensaje_whatsapp(data)
    save_message(wa_id, "Admin", "admin", text)
    return redirect(url_for("chat_view", wa_id=wa_id))


@app.route("/api/chat/<wa_id>/messages")
def api_get_messages(wa_id):
    messages = get_chat(wa_id)
    return {
        "messages": [
            {"sender": m[0], "message": m[1], "timestamp": m[2]}
            for m in messages
        ]
    }


# =====================
# WEBHOOK
# =====================

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == TOKEN:
        return request.args.get("hub.challenge")
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    entry = body["entry"][0]
    changes = entry["changes"][0]
    value = changes["value"]
    messages = value.get("messages", [])

    if not messages:
        return "OK", 200

    msg = messages[0]
    number = services.replace_start(msg["from"])
    messageId = msg["id"]
    name = value["contacts"][0]["profile"]["name"]

    text = services.obtener_Mensaje_whatsapp(msg)
    save_message(number, name, "usuario", text)

    services.administrar_chatbot(text, number, messageId, name)
    return "OK", 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
