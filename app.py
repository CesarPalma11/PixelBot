import os
from flask import Flask, request, render_template, redirect, url_for
import services
from database import init_db, get_recent_chats, get_chat, save_message, set_handoff

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


# 🔄 BOTÓN CERRAR CHAT
@app.route("/chat/<wa_id>/close", methods=["POST"])
def close_chat(wa_id):
    set_handoff(wa_id, False)
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
    return redirect(url_for("chat_view", wa_id=wa_id))


@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == TOKEN:
        return request.args.get("hub.challenge")
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    msg = body["entry"][0]["changes"][0]["value"]["messages"][0]
    number = services.replace_start(msg["from"])
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    text = services.obtener_Mensaje_whatsapp(msg)
    save_message(number, name, "usuario", text)
    services.administrar_chatbot(text, number, msg["id"], name)
    return "OK", 200
