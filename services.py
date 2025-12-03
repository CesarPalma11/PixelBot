import requests
import os
import json
import time

# =========================
# CONFIGURACIÓN DESDE ENV
# =========================
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
DOCUMENT_URL = os.getenv("DOCUMENT_URL")

# Stickers (pueden quedar aquí o en env)
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
# FUNCIONES DE MENSAJES
# =========================
def obtener_Mensaje_whatsapp(message):
    print("Mensaje recibido raw:", message)
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

def enviar_Mensaje_whatsapp(data):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {WHATSAPP_TOKEN}'
        }
        print("Enviando al API de WhatsApp:", data)
        response = requests.post(WHATSAPP_URL, headers=headers, data=data)
        print("Respuesta WhatsApp:", response.status_code, response.text)
        return response.status_code
    except Exception as e:
        print("Error enviando mensaje:", e)
        return 403

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
    rows = [{"id": f"{sedd}_row_{i+1}", "title": option, "description": ""}
            for i, option in enumerate(options)]
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

def document_Message(number, url, caption, filename):
    if url is None:
        url = DOCUMENT_URL
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
        return STICKERS.get(media_name, None)
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

# =========================
# LOGICA DEL CHATBOT
# =========================
def administrar_chatbot(text, number, messageId, name):
    text_lower = text.lower()
    queue = []
    print("Procesando mensaje usuario:", text_lower)

    # Marcar el mensaje como leído
    queue.append(markRead_Message(messageId))
    time.sleep(0.5)

    # =============================
    # MENSAJE DE BIENVENIDA
    # =============================
    if "hola" in text_lower:
        body = "¡Hola! Soy PixelBot 👋, en qué puedo ayudarte?"
        footer = "Equipo PixelBot"
        options = ["Quiero automatizar mi WhatsApp", "Quiero una página web"]
        queue.append(replyReaction_Message(number, messageId, "🤖"))
        queue.append(buttonReply_Message(number, options, body, footer, "menu_principal", messageId))

    # =============================
    # OPCIONES PRINCIPALES
    # =============================
    elif "quiero automatizar mi whatsapp" in text_lower:
        body = "Perfecto! ¿Qué tipo de automatización te interesa?"
        footer = "Automatización WhatsApp"
        options = [
            "Respuestas automáticas",
            "Menú interactivo con botones",
            "Integración con base de datos",
            "Notificaciones y alertas"
        ]
        queue.append(buttonReply_Message(number, options, body, footer, "auto_whatsapp", messageId))

    elif "quiero una página web" in text_lower:
        body = "¡Genial! ¿Qué tipo de página web deseas crear?"
        footer = "Servicios Web"
        options = [
            "Página corporativa",
            "Tienda online (e-commerce)",
            "Landing page para campaña",
            "Blog personal o profesional"
        ]
        queue.append(buttonReply_Message(number, options, body, footer, "web_opciones", messageId))

    # =============================
    # SUBMENÚ: Automatización WhatsApp
    # =============================
    elif "respuestas automáticas" in text_lower:
        body = "Las respuestas automáticas permiten contestar a tus clientes sin estar presente. Puedes configurar:"
        footer = "Automatización WhatsApp"
        options = [
            "Responder preguntas frecuentes",
            "Mensajes de bienvenida",
            "Responder fuera de horario"
        ]
        queue.append(listReply_Message(number, options, body, footer, "auto_resp", messageId))

    elif "menú interactivo con botones" in text_lower:
        body = "Puedes crear menús con botones para que tus clientes naveguen fácilmente. Ejemplos:"
        footer = "Automatización WhatsApp"
        options = ["Servicios", "Soporte", "Contacto"]
        queue.append(listReply_Message(number, options, body, footer, "auto_menu", messageId))

    elif "integración con base de datos" in text_lower:
        queue.append(text_Message(number, "Podemos conectar tu WhatsApp con tu base de datos para consultas automáticas, reportes y seguimiento de clientes."))

    elif "notificaciones y alertas" in text_lower:
        queue.append(text_Message(number, "Podemos enviar notificaciones automáticas a tus clientes: confirmaciones de pedido, recordatorios, alertas importantes."))

    # =============================
    # SUBMENÚ: Página web
    # =============================
    elif "página corporativa" in text_lower:
        queue.append(text_Message(number, "Una página corporativa te permitirá mostrar tu empresa, servicios y contacto profesional."))

    elif "tienda online" in text_lower:
        queue.append(text_Message(number, "Podemos crear tu tienda online con carrito de compras, pasarela de pagos y gestión de productos."))

    elif "landing page" in text_lower:
        queue.append(text_Message(number, "Una landing page efectiva para tus campañas de marketing o captación de leads."))

    elif "blog personal" in text_lower:
        queue.append(text_Message(number, "Podemos crear un blog con contenido dinámico, diseño responsivo y fácil de actualizar."))

    # =============================
    # MENSAJE POR DEFECTO
    # =============================
    else:
        queue.append(text_Message(number, "Lo siento, no entendí tu mensaje. Escribe 'hola' para empezar de nuevo."))

    # =============================
    # ENVIAR MENSAJES
    # =============================
    for item in queue:
        enviar_Mensaje_whatsapp(item)


# =========================
# FUNCIÓN AUXILIAR
# =========================
def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
