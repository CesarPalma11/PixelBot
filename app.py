import os
from flask import Flask, request, render_template, redirect, url_for
import services
from database import init_db, get_recent_chats, get_chat, save_message, set_handoff, disable_handoff

app = Flask(__name__)
init_db()

TOKEN = os.getenv("TOKEN")


@app.route("/")
def dashboard():
    chats = get_recent_chats()
    return render_template("index.html", chats=chats)


@app.route("/chat/<wa_id>")
def chat_view(wa_id):
    messages = get_chat(wa_id)
    return render_template("chat.html", wa_id=wa_id, messages=messages)


@app.route("/chat/<wa_id>/close", methods=["POST"])
def close_chat(wa_id):
    disable_handoff(wa_id)
    services.enviar_Mensaje_whatsapp(
        services.text_Message(
            wa_id,
            "🤖 El bot volvió a activarse.\nEscribí *hola* para continuar."
        )
    )
    return redirect(url_for("chat_view", wa_id=wa_id))


@app.route("/send_message/<wa_id>", methods=["POST"])
def send_message_panel(wa_id):
    text = request.form.get("text")
    services.enviar_Mensaje_whatsapp(services.text_Message(wa_id, text))
    save_message(wa_id, "Admin", "admin", text)
    return "", 204


@app.route("/api/chat/<wa_id>/messages")
def api_chat_messages(wa_id):
    messages = get_chat(wa_id)
    return {
        "messages": [
            {"sender": m[0], "message": m[1], "timestamp": m[2]}
            for m in messages
        ]
    }


@app.route("/api/recent_chats")
def api_recent_chats():
    chats = get_recent_chats()
    return {
        "chats": [
            {"wa_id": c[0], "name": c[1], "timestamp": c[2]}
            for c in chats
        ]
    }


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    print("📩 Webhook:", body)

    try:
        value = body["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "OK", 200

        msg = value["messages"][0]
        contact = value.get("contacts", [{}])[0]

        number = services.replace_start(msg["from"])
        name = contact.get("profile", {}).get("name", "")
        text = services.obtener_Mensaje_whatsapp(msg)

        save_message(number, name, "usuario", text)
        services.administrar_chatbot(text, number, msg.get("id"), name)

    except Exception as e:
        print("❌ Error webhook:", e)

    return "OK", 200


@app.route("/chat/<wa_id>/handoff/<int:minutes>", methods=["POST"])
def handoff_timed(wa_id, minutes):
    set_handoff(wa_id, minutes=minutes)
    return redirect(url_for("chat_view", wa_id=wa_id))


@app.route("/api/chat/<wa_id>/status")
def api_chat_status(wa_id):
    from database import get_chat_status
    return {"status": get_chat_status(wa_id)}
