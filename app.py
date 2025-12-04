from flask import Flask, request, render_template
import os
import services
from database import get_recent_chats, get_chat, save_message, init_db

app = Flask(__name__)

# Token de verificación del webhook (Meta)
TOKEN = os.getenv("TOKEN")


# ==============================
#     PANEL — DASHBOARD
# ==============================
@app.route("/")
def dashboard():
    chats = get_recent_chats()
    return render_template("index.html", chats=chats)


@app.route("/chat/<wa_id>")
def chat_view(wa_id):
    messages = get_chat(wa_id)
    return render_template("chat.html", wa_id=wa_id, messages=messages)


# ==============================
#         RUTA TEST
# ==============================
@app.route('/bienvenido', methods=['GET'])
def bienvenido():
    return 'Hola mundo!'


# ==============================
#     WEBHOOK — GET
# ==============================
@app.route('/webhook', methods=['GET'])
def verificar_token():
    """
    Verifica el token de Meta al configurar el webhook.
    """
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == TOKEN and challenge is not None:
            print("Webhook verificado correctamente.")
            return challenge
        else:
            print("Token incorrecto recibido:", token)
            return 'token incorrecto', 403

    except Exception as e:
        print("Error verificando token:", e)
        return str(e), 403


# ==============================
#     WEBHOOK — POST
# ==============================
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    """
    Recibe mensajes de WhatsApp y los procesa con servicios.py
    """
    try:
        body = request.get_json()
        print("Webhook recibido:", body)

        entry = body.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        messages = value.get('messages', [])

        if not messages:
            print("No hay mensajes en el payload.")
            return 'No hay mensajes', 200

        # Datos del mensaje
        message = messages[0]
        number = message.get('from')
        number = services.replace_start(number)
        messageId = message.get('id')

        contacts = value.get('contacts', [{}])[0]
        name = contacts.get('profile', {}).get('name', "")

        text = services.obtener_Mensaje_whatsapp(message)

        print(f"Procesando mensaje de {number} ({name}): {text}")

        # Guardar mensaje del usuario
        save_message(number, name, "usuario", text)

        # Responder chatbot
        bot_response = services.administrar_chatbot(text, number, messageId, name)

        # Guardar respuesta del bot SI ES TEXTO
        if bot_response:
            save_message(number, name, "bot", bot_response)

        return 'enviado', 200

    except Exception as e:
        print("Error procesando mensaje:", e)
        return 'no enviado: ' + str(e), 500


# ==============================
#   INICIAR APP — LOCAL/RENDER
# ==============================
if __name__ == '__main__':
    init_db()  # crea base de datos si no existe
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
