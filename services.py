import requests
import os
import json
import time
import sett  # archivo con tus variables de entorno: WHATSAPP_TOKEN, PHONE_NUMBER_ID, DOCUMENT_URL, etc.

# ===========================================
# Mensajes y medios
# ===========================================
STICKERS = sett.stickers  # stickers definidos en sett.py

# ===========================================
# Funciones para obtener mensajes
# ===========================================
def obtener_Mensaje_whatsapp(message):
    if 'type' not in message:
        return 'mensaje no reconocido'

    typeMessage = message['type']
    if typeMessage == 'text':
        return message['text']['body']
    elif typeMessage == 'button':
        return message['button']['text']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'list_reply':
        return message['interactive']['list_reply']['title']
    elif typeMessage == 'interactive' and message['interactive']['type'] == 'button_reply':
        return message['interactive']['button_reply']['title']
    else:
        return 'mensaje no procesado'

# ===========================================
# Función robusta para enviar mensajes
# ===========================================
def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = sett.whatsapp_token
        PHONE_NUMBER_ID = sett.PHONE_NUMBER_ID
        whatsapp_url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {whatsapp_token}'
        }

        print("Enviando mensaje a WhatsApp:", data)
        response = requests.post(whatsapp_url, headers=headers, data=data)

        # Log completo de la respuesta
        print("STATUS CODE:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return f'Error al enviar mensaje: {response.text}', response.status_code

    except Exception as e:
        print("EXCEPCION:", str(e))
        return str(e), 403

# ===========================================
# Funciones de creación de mensajes
# ===========================================
def text_Message(number, text):
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "text",
        "text": {"body": text}
    })


def buttonReply_Message(number, options, body, footer, sedd, messageId):
    buttons = [{"type": "reply", "reply": {"id": f"{sedd}_btn_{i+1}", "title": option}}
               for i, option in enumerate(options)]
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {"buttons": buttons}
        }
    })


def listReply_Message(number, options, body, footer, sedd, messageId):
    rows = [{"id": f"{sedd}_row_{i+1}", "title": option, "description": ""} for i, option in enumerate(options)]
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {"button": "Ver Opciones", "sections": [{"title": "Secciones", "rows": rows}]}
        }
    })


def document_Message(number, url=None, caption="", filename="document.pdf"):
    if url is None:
        url = sett.DOCUMENT_URL
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "document",
        "document": {"url": url, "caption": caption, "filename": filename}
    })


def sticker_Message(number, sticker_id):
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "sticker",
        "sticker": {"id": sticker_id}
    })


def get_media_id(media_name, media_type):
    if media_type == "sticker":
        return STICKERS.get(media_name)
    return None


def replyReaction_Message(number, messageId, emoji):
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "reaction",
        "reaction": {"message_id": messageId, "emoji": emoji}
    })


def replyText_Message(number, messageId, text):
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "context": {"message_id": messageId},
        "type": "text",
        "text": {"body": text}
    })


def markRead_Message(messageId):
    return json.dumps({
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": messageId
    })

# ===========================================
# Chatbot
# ===========================================
def administrar_chatbot(text, number, messageId, name):
    text = text.lower()
    queue = []
    print("Mensaje del usuario:", text)

    queue.append(markRead_Message(messageId))
    time.sleep(1)

    # Aquí van tus condiciones de flujo como antes...
    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a Bigdateros. ¿Cómo podemos ayudarte hoy?"
        footer = "Equipo Bigdateros"
        options = ["✅ servicios", "📅 agendar cita"]
        queue.append(replyReaction_Message(number, messageId, "🫡"))
        queue.append(buttonReply_Message(number, options, body, footer, "sed1", messageId))

    # ... resto de tus flujos ...

    for item in queue:
        enviar_Mensaje_whatsapp(item)

# ===========================================
# Función para corregir prefijo internacional
# ===========================================
def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
