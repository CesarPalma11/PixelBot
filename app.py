from flask import Flask, request, render_template, redirect, url_for
import os
import services
from database import get_recent_chats, get_chat, save_message, init_db

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


@app.route("/send_message/<wa_id>", methods=["POST"])
def send_message_panel(wa_id):
    text = request.form.get("text")
    messages = get_chat(wa_id)
    name = messages[-1][1] if messages else "Usuario"

    data = services.text_Message(wa_id, text)
    services.enviar_Mensaje_whatsapp(data)
    save_message(wa_id, name, "bot", text)
    
    return redirect(url_for("chat_view", wa_id=wa_id))
