import requests
import os
import json
import time

# Configuración desde variables de entorno
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
DOCUMENT_URL = os.getenv("DOCUMENT_URL")  # opcional si quieres cargar desde env

# Stickers (puedes mantenerlo aquí o moverlo a env)
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


def enviar_Mensaje_whatsapp(data):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {WHATSAPP_TOKEN}'
        }
        print("Enviando: ", data)
        response = requests.post(WHATSAPP_URL, headers=headers, data=data)

        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return str(e), 403


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


def administrar_chatbot(text, number, messageId, name):
    text = text.lower()
    queue = []
    print("Mensaje del usuario:", text)

    queue.append(markRead_Message(messageId))
    time.sleep(2)

    if "hola" in text:
        body = "¡Hola! 👋 Bienvenido a Bigdateros. ¿Cómo podemos ayudarte hoy?"
        footer = "Equipo Bigdateros"
        options = ["✅ servicios", "📅 agendar cita"]

        queue.append(replyReaction_Message(number, messageId, "🫡"))
        queue.append(buttonReply_Message(number, options, body, footer, "sed1", messageId))

    elif "servicios" in text:
        body = "Tenemos varias áreas de consulta para elegir. ¿Cuál de estos servicios te gustaría explorar?"
        footer = "Equipo Bigdateros"
        options = ["Analítica Avanzada", "Migración Cloud", "Inteligencia de Negocio"]

        queue.append(listReply_Message(number, options, body, footer, "sed2", messageId))
        queue.append(sticker_Message(number, get_media_id("perro_traje", "sticker")))

    elif "inteligencia de negocio" in text:
        body = "Buenísima elección. ¿Te gustaría que te enviara un documento PDF con una introducción a nuestros métodos de Inteligencia de Negocio?"
        footer = "Equipo Bigdateros"
        options = ["✅ Sí, envía el PDF.", "⛔ No, gracias"]
        queue.append(buttonReply_Message(number, options, body, footer, "sed3", messageId))

    elif "sí, envía el pdf" in text:
        queue.append(sticker_Message(number, get_media_id("pelfet", "sticker")))
        queue.append(text_Message(number, "Genial, por favor espera un momento."))
        time.sleep(3)
        queue.append(document_Message(number, None, "Listo 👍🏻", "Inteligencia de Negocio.pdf"))
        time.sleep(3)
        body = "¿Te gustaría programar una reunión con uno de nuestros especialistas para discutir estos servicios más a fondo?"
        footer = "Equipo Bigdateros"
        options = ["✅ Sí, agenda reunión", "No, gracias."]
        queue.append(buttonReply_Message(number, options, body, footer, "sed4", messageId))

    elif "sí, agenda reunión" in text:
        body = "Estupendo. Por favor, selecciona una fecha y hora para la reunión:"
        footer = "Equipo Bigdateros"
        options = ["📅 10: mañana 10:00 AM", "📅 7 de junio, 2:00 PM", "📅 8 de junio, 4:00 PM"]
        queue.append(listReply_Message(number, options, body, footer, "sed5", messageId))

    elif "7 de junio, 2:00 pm" in text:
        body = "Excelente, has seleccionado la reunión para el 7 de junio a las 2:00 PM. Te enviaré un recordatorio un día antes. ¿Necesitas ayuda con algo más hoy?"
        footer = "Equipo Bigdateros"
        options = ["✅ Sí, por favor", "❌ No, gracias."]
        queue.append(buttonReply_Message(number, options, body, footer, "sed6", messageId))

    elif "no, gracias." in text:
        queue.append(text_Message(number, "Perfecto! No dudes en contactarnos si tienes más preguntas. Recuerda que también ofrecemos material gratuito para la comunidad. ¡Hasta luego! 😊"))

    else:
        queue.append(text_Message(number, "Lo siento, no entendí lo que dijiste. ¿Quieres que te ayude con alguna de estas opciones?"))

    for item in queue:
        enviar_Mensaje_whatsapp(item)


# Solución de prefijo para México y Argentina
def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
