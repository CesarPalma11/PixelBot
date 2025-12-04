import requests
import os
import json
import time
from database import save_message  # <-- Guardar mensajes en DB

# =========================
# CONFIGURACIÓN DESDE ENV
# =========================
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
DOCUMENT_URL = os.getenv("DOCUMENT_URL")

# Stickers
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

    t = message['type']
    if t == 'text':
        return message['text']['body']
    elif t == 'button':
        return message['button']['text']
    elif t == 'interactive' and message['interactive']['type'] == 'list_reply':
        return message['interactive']['list_reply']['title']
    elif t == 'interactive' and message['interactive']['type'] == 'button_reply':
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
        resp = requests.post(WHATSAPP_URL, headers=headers, data=data)
        print("Respuesta WhatsApp:", resp.status_code, resp.text)
        return resp.status_code
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

    # Marcar como leído
    queue.append(markRead_Message(messageId))
    time.sleep(0.5)

    # -----------------
    # Mensaje de bienvenida
    # -----------------
    if "hola" in text_lower:
        body = "¡Hola! Soy PixelBot 👋, en qué puedo ayudarte?"
        footer = "Equipo PixelBot"
        options = ["Automatizar WhatsApp", "Crear página web", "Soporte / Consultas"]
        queue.append(replyReaction_Message(number, messageId, "🤖"))
        queue.append(buttonReply_Message(number, options, body, footer, "menu_principal", messageId))

    elif "automatizar" in text_lower:
        body = "Elige qué tipo de automatización deseas:"
        footer = "Automatizaciones"
        options = ["Chatbot básico", "Respuestas automáticas", "Enviar documentos", "Integraciones externas"]
        queue.append(listReply_Message(number, options, body, footer, "automatizar", messageId))

    elif "página web" in text_lower or "crear" in text_lower:
        body = "Selecciona el tipo de página que deseas:"
        footer = "Servicios Web"
        options = ["Landing page", "E-commerce", "Portafolio personal", "Blog / Noticias"]
        queue.append(listReply_Message(number, options, body, footer, "web", messageId))

    elif "soporte" in text_lower or "consultas" in text_lower:
        body = "Elige una opción de soporte:"
        footer = "Soporte PixelBot"
        options = ["Precios", "Horarios de atención", "Contacto directo"]
        queue.append(listReply_Message(number, options, body, footer, "soporte", messageId))

    # -----------------
    # Respuestas específicas
    # -----------------
    response_map = {
        "chatbot básico": "Un chatbot básico puede responder preguntas frecuentes automáticamente.",
        "respuestas automáticas": "Podemos configurar respuestas automáticas según palabras clave.",
        "enviar documentos": "Puedes enviar documentos automáticamente a tus clientes.",
        "integraciones externas": "Integramos tu WhatsApp con CRM, Google Sheets y más.",
        "landing page": "Creamos páginas simples para promocionar tu negocio.",
        "e-commerce": "Creamos tiendas online completas con carrito de compras.",
        "portafolio personal": "Diseñamos un portafolio profesional para mostrar tus proyectos.",
        "blog / noticias": "Creamos blogs para publicar noticias y artículos fácilmente.",
        "precios": "Nuestros precios varían según el servicio, contáctanos para más info.",
        "horarios": "Atendemos de lunes a viernes de 9 a 18 hs.",
        "contacto directo": "Puedes escribirnos a contacto@bigdateros.com o llamar al +54 9 11 6018-5717"
    }

    if text_lower in response_map:
        resp = response_map[text_lower]
        queue.append(text_Message(number, resp))

    # -----------------
    # Fallback
    # -----------------
    if not queue:
        queue.append(text_Message(number, "Lo siento, no entendí tu mensaje. Escribe 'hola' para comenzar."))

    # -----------------
    # Enviar y guardar todos los mensajes en DB
    # -----------------
    for item in queue:
        enviar_Mensaje_whatsapp(item)
        # Guardar respuesta del bot en DB si es texto
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
