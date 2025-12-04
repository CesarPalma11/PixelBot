from flask import Flask, request, render_template, redirect, url_for
import os
import services
from database import get_recent_chats, get_chat, save_message, init_db

app = Flask(__name__)
init_db()

TOKEN = os.getenv("TOKEN")


# =====================================
#              DASHBOARD
# =====================================
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


# =====================================
#               WEBHOOK
# =====================================

# Aceptar /webhook y /webhook/
@app.route("/webhook", methods=["GET", "POST"])
@app.route("/webhook/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verificar token de Meta
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if token == TOKEN:
            return challenge or "OK", 200
        return "Token incorrecto", 403

    else:
        # Recibir mensajes de WhatsApp (POST)
        try:
            body = request.get_json()
            print("Webhook recibido:", body)

            entry = body.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if not messages:
                return "No hay mensajes", 200

            message = messages[0]
            number = message.get("from")
            number = services.replace_start(number)
            messageId = message.get("id")

            contacts = value.get("contacts", [{}])[0]
            name = contacts.get("profile", {}).get("name", "")

            text = services.obtener_Mensaje_whatsapp(message)

            save_message(number, name, "usuario", text)

            bot_response = services.administrar_chatbot(text, number, messageId, name)

            if bot_response:
                save_message(number, name, "bot", bot_response)

            return "enviado", 200

        except Exception as e:
            print("Error procesando mensaje:", e)
            return "error: " + str(e), 500


# =====================================
#             RUN SERVER
# =====================================
# Necesario para funcionar en Render
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
