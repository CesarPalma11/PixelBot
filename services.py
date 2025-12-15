import requests
import os
import json
import time
from database import save_message, set_handoff, is_handoff

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"


# =====================
# ENVÍO A WHATSAPP
# =====================

def enviar_Mensaje_whatsapp(data):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = json.loads(data)
    print("➡️ Enviando:", payload)
    res = requests.post(WHATSAPP_URL, json=payload, headers=headers)
    print("⬅️ Respuesta:", res.status_code, res.text)
    return res.status_code


# =====================
# FORMATOS
# =====================

def text_Message(number, text):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {"body": text}
    })


def buttonReply_Message(number, options, body, footer, sedd, messageId):
    buttons = [
        {"type": "reply", "reply": {"id": f"{sedd}_{i}", "title": opt}}
        for i, opt in enumerate(options, start=1)
    ]
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


def markRead_Message(messageId):
    return json.dumps({
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": messageId
    })


# =====================
# MENSAJE ENTRANTE
# =====================

def obtener_Mensaje_whatsapp(message):
    t = message.get("type")
    if t == "text":
        return message["text"]["body"]
    if t == "button":
        return message["button"]["text"]
    if t == "interactive":
        ir = message["interactive"]
        if ir["type"] == "button_reply":
            return ir["button_reply"]["title"]
    return ""


# =====================
# LÓGICA DEL BOT
# =====================

def administrar_chatbot(text, number, messageId, name):

    text_lower = text.lower().strip()

    # 🔴 BOT APAGADO
    if is_handoff(number):
        print("🛑 Handoff activo, bot deshabilitado")
        return False

    enviar_Mensaje_whatsapp(markRead_Message(messageId))
    time.sleep(0.2)

    # 👤 PEDIR ASESOR
    if text_lower in ["asesor", "humano", "persona", "hablar con alguien"]:
        set_handoff(number, True)
        enviar_Mensaje_whatsapp(text_Message(
            number,
            "👤 Te comunico con un asesor. En breve alguien del equipo te responde."
        ))
        save_message(number, name, "bot", "Handoff a asesor")
        return True

    # 👋 MENÚ PRINCIPAL
    if "hola" in text_lower:
        enviar_Mensaje_whatsapp(buttonReply_Message(
            number,
            ["Ver productos", "Soporte", "Estado de mi pedido"],
            "👋 Hola, ¿en qué puedo ayudarte?\n\n"
            "✍️ Escribí *asesor* para hablar con una persona 👤",
            "Equipo PixelBot",
            "menu",
            messageId
        ))
        return True

    respuestas = {
        "ver productos": "🛒 Estos son nuestros productos...",
        "soporte": "🛠️ Contame qué problema tenés.",
        "estado de mi pedido": "📦 Decime tu número de pedido."
    }

    if text_lower in respuestas:
        enviar_Mensaje_whatsapp(text_Message(number, respuestas[text_lower]))
        save_message(number, name, "bot", respuestas[text_lower])
        return True

    enviar_Mensaje_whatsapp(text_Message(
        number,
        "No entendí tu mensaje. Escribí *hola* para ver el menú."
    ))
    return True


def replace_start(s):
    if s.startswith("549"):
        return "54" + s[3:]
    return s
