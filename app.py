from flask import Flask, request, render_template
import os
import services
from database import get_recent_chats, get_chat, save_message, init_db

app = Flask(__name__)
TOKEN = os.getenv("TOKEN")

# ===== DASHBOARD =====
@app.route("/")
def dashboard():
    chats = get_recent_chats()
    return render_template("index.html", chats=chats)

@app.route("/chat/<wa_id>")
def chat_view(wa_id):
    messages = get_chat(wa_id)
    return render_template("chat.html", wa_id=wa_id, messages=messages)

# ===== RUTA TEST =====
@app.route('/bienvenido', methods=['GET'])
def bienvenido():
    return 'Hola mundo!'

# ===== WEBHOOK GET =====
@app.route('/webhook', methods=['GET'])
def verificar_token():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if token == TOKEN and challenge:
        return challenge
    return 'token incorrecto', 403

# ===== WEBHOOK POST =====
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    body = request.get_json()
    entry = body.get('entry', [])[0]
    changes = entry.get('changes', [])[0]
    value = changes.get('value', {})
    messages = value.get('messages', [])

    if not messages:
        return 'No hay mensajes', 200

    message = messages[0]
    number = services.replace_start(message.get('from'))
    messageId = message.get('id')
    name = value.get('contacts', [{}])[0].get('profile', {}).get('name', "")

    text = services.obtener_Mensaje_whatsapp(message)

    save_message(number, name, "usuario", text)

    bot_response = services.administrar_chatbot(text, number, messageId, name)

    if bot_response:
        save_message(number, name, "bot", bot_response)

    return 'enviado', 200

# ===== INICIO =====
if __name__ == '__main__':
    init_db()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
