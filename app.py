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
    print("📩 Webhook recibido:", body)

    try:
        entry = body.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})

        # 🚫 Si NO hay mensajes, ignorar (statuses, read, etc.)
        if "messages" not in value:
            return "EVENTO SIN MENSAJE", 200

        message = value["messages"][0]
        contact = value.get("contacts", [{}])[0]

        number = services.replace_start(message.get("from"))
        name = contact.get("profile", {}).get("name", "")

        text = services.obtener_Mensaje_whatsapp(message)

        save_message(number, name, "usuario", text)

        services.administrar_chatbot(
            text,
            number,
            message.get("id"),
            name
        )

    except Exception as e:
        print("❌ Error procesando webhook:", e)

    return "OK", 200


@app.route("/api/recent_chats")
def api_recent_chats():
    chats = get_recent_chats()
    return {
        "chats": [
            {
                "wa_id": c[0],
                "name": c[1],
                "timestamp": c[2]
            }
            for c in chats
        ]
    }
