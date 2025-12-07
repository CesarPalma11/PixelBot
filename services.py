import requests
import os
import json
import time
from database import save_message  # Guardar mensajes en DB

# =========================
# CONFIGURACIÓN DESDE ENV
# =========================
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
DOCUMENT_URL = os.getenv("DOCUMENT_URL")

# Stickers predefinidos
STICKERS = {
    "poyo_feliz": 984778742532668,
    "perro_traje": 1009219236749949,
    "perro_triste": 982264672785815,
    "pedro_pascal_love": 801721017874258,
    "pelfet": 3127736384038169,
    "anotado": 24039533498978939,
    "gato_festejando": 1736736493414401,
    "okis": 268811655677102,
    "cachetada": 275511571531644,
    "gato_juzgando": 107235069063072,
    "chicorita": 3431648470417135,
    "gato_triste": 210492141865964,
    "gato_cansado": 1021308728970759
}

# =========================
# FUNCIONES MEDIA
# =========================

def get_media_url(media_id):
    url = f"https://graph.facebook.com/v22.0/{media_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    res = requests.get(url, headers=headers).json()

    print("MEDIA URL RESPONSE:", res)

    return res["url"]  # WhatsApp devuelve link temporal


# =========================
# OBTENER MENSAJE SEGÚN TIPO
# =========================

def obtener_Mensaje_whatsapp(message):
    print("Mensaje recibido raw:", message)
    if 'type' not in message:
        return 'mensaje no reconocido'

    t = message['type']

    if t == 'text':
        return message['text']['body']

    if t == 'sticker':
        return "[sticker]"

    if t == 'button':
        return message['button']['text']

    if t == 'interactive' and message['interactive']['type'] == 'list_reply':
        return message['interactive']['list_reply']['title']

    if t == 'interactive' and message['interactive']['type'] == 'button_reply':
        return message['interactive']['button_reply']['title']

    return 'mensaje no procesado'


# =========================
# ENVIAR MENSAJES
# =========================

def enviar_Mensaje_whatsapp(data):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {WHATSAPP_TOKEN}'
        }
        print("Enviando al API de WhatsApp:", data)
        resp = requests.post(WHATSAPP_URL, headers=headers, data=data)
        print("Respuesta WhatsApp:", resp.status_code, resp.text)
        return resp.status_code
    except Exception as e:
        print("Error enviando mensaje:", e)
        return 403


# =========================
# FORMATO DE MENSAJES
# =========================

def text_Message(number, text):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {"body": text}
    })


def sticker_Message(number, sticker_id):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "sticker",
        "sticker": {"id": sticker_id}
    })


def buttonReply_Message(number, options, body, footer, sedd, messageId):
    buttons = [{"type": "reply", "reply": {"id": f"{sedd}_btn_{i+1}", "title": option}}
               for i, option in enumerate(options)]
    return json.dumps({
        "messaging_product": "whatsapp",
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
    rows = [{"id": f"{sedd}_row_{i+1}", "title": option, "description": ""}
            for i, option in enumerate(options)]

    return json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {
                "button": "Ver Opciones",
                "sections": [{"title": "Secciones", "rows": rows}]
            }
        }
    })


def replyReaction_Message(number, messageId, emoji):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "reaction",
        "reaction": {"message_id": messageId, "emoji": emoji}
    })


def markRead_Message(messageId):
    return json.dumps({
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": messageId
    })


# =========================
# LÓGICA PRINCIPAL DEL BOT
# =========================

def administrar_chatbot(text, number, messageId, name):

    text_lower = text.lower()
    queue = []

    print("Procesando mensaje usuario:", text_lower)

    # Marcar como leído
    queue.append(markRead_Message(messageId))
    time.sleep(0.3)

    # Menú principal
    if "hola" in text_lower:
        queue.append(replyReaction_Message(number, messageId, "🤖"))
        queue.append(buttonReply_Message(
            number,
            ["Automatizar WhatsApp", "Crear página web", "Soporte / Consultas"],
            "¡Hola! Soy PixelBot 👋 ¿en qué puedo ayudarte?",
            "Equipo PixelBot",
            "menu_principal",
            messageId
        ))

    # Respuestas simples
    response_map = {
        "automatizar whatsapp": "Podemos automatizar tu WhatsApp con bots, respuestas rápidas y más.",
        "chatbot básico": "Un chatbot básico responde preguntas frecuentes automáticamente.",
        "respuestas automáticas": "Podemos configurar respuestas automáticas según palabras clave.",
        "crear página web": "Creamos sitios web modernos y rápidos para tu negocio.",
        "soporte": "Estoy aquí para ayudarte. ¿Qué necesitas saber?",
    }

    if text_lower in response_map:
        queue.append(text_Message(number, response_map[text_lower]))

    # Fallback
    if not queue:
        queue.append(text_Message(number, "No entendí tu mensaje. Escribe *hola* para ver el menú."))

    # Enviar y guardar respuestas
    for item in queue:
        enviar_Mensaje_whatsapp(item)

        try:
            data_json = json.loads(item)
            if data_json.get("type") == "text":
                save_message(number, name, "bot", data_json["text"]["body"])
        except:
            pass

    return True


# =========================
# AUXILIAR
# =========================

def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
