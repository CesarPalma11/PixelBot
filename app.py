from flask import Flask, request, render_template, redirect, url_for
import os
import services
from database import get_recent_chats, get_chat, save_message, init_db

app = Flask(__name__)

# ==============================
#   INICIALIZAR BASE DE DATOS
# ==============================
init_db()  # Se ejecuta siempre, incluso en Render

# ==============================
#     TOKEN WEBHOOK
# ==============================
TOKEN = os.getenv("TOKEN")


# ==============================
#     DASHBOARD — Chats recientes
# ==============================
@app.route("/")
def dashboard():
    chats = get_recent_chats()
    return render_template("index.html", chats=chats)


# ==============================
#     CHAT VIEW
# ==============================
@app.route("/chat/<wa_id>")
def chat_view(wa_id):
    messages = get_chat(wa_id)
    return render_template("chat.html", wa_id=wa_id, messages=messages)


# ==============================
#     ENVIAR MENSAJE DESDE PANEL
# ==============================
@app.route("/send_message/<wa_id>", methods=["POST"])
def send_message_panel(wa_id):
    text = request.form.get("text")
    messages = get_chat(wa_id)
    name = messages[-1][1] if messages else "Usuario"

    # Crear mensaje JSON para WhatsApp
    data = services.text_Message(wa_id, text)
    services.enviar_Mensaje_whatsapp(data)

    # Guardamos solo el mensaje del USUARIO
    save_message(wa_id, name, "usuario", text)
    
    return redirect(url_for("chat_view", wa_id=wa_id))


# ==============================
#     RUTA DE TEST
# ==============================
@app.route('/bienvenido', methods=['GET'])
def bienvenido():
    return 'Hola mundo!'


# ==============================
#     WEBHOOK — GET (Verificación)
# ==============================
@app.route('/webhook', methods=['GET'])
def verificar_token():
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
#     WEBHOOK — POST (Recibir mensajes)
# ==============================
@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    """
    Recibe mensajes de WhatsApp y los procesa con services.py
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
        services.administrar_chatbot(text, number, messageId, name)

        return 'enviado', 200

    except Exception as e:
        print("Error procesando mensaje:", e)
        return 'no enviado: ' + str(e), 500


# ==============================
#   INICIAR APP — LOCAL/RENDER
# ==============================
if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
