import os
import json
import requests
from database import save_message, set_handoff, is_handoff

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"


def enviar_Mensaje_whatsapp(data):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = json.loads(data)
    res = requests.post(WHATSAPP_URL, json=payload, headers=headers)
    print("WA:", res.status_code, res.text)
    return res.status_code


def text_Message(number, text):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {"body": text}
    })


def buttonReply_Message(number, options, body):
    buttons = [
        {"type": "reply", "reply": {"id": str(i), "title": o}}
        for i, o in enumerate(options, 1)
    ]
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": buttons}
        }
    })


def obtener_Mensaje_whatsapp(msg):
    if msg["type"] == "text":
        return msg["text"]["body"]
    if msg["type"] == "button":
        return msg["button"]["text"]
    if msg["type"] == "interactive":
        return msg["interactive"]["button_reply"]["title"]
    return ""


def administrar_chatbot(text, number, messageId, name):
    text = text.lower().strip()

    # 👤 humano activo
    if is_handoff(number):
        print("👤 Modo humano activo")
        return

    # 👉 pedir asesor
    if text in ["asesor", "hablar con una persona"]:
        set_handoff(number, minutes=60)
        enviar_Mensaje_whatsapp(text_Message(
            number,
            "👤 Te paso con un asesor.\n🤖 El bot se reactivará automáticamente en 1 hora."
        ))
        save_message(number, name, "bot", "handoff activado")
        return

    if "hola" in text:
        enviar_Mensaje_whatsapp(buttonReply_Message(
            number,
            ["Ver productos", "Soporte", "Estado de mi pedido"],
            "👋 Hola, ¿en qué puedo ayudarte?\n\nEscribí *asesor* para hablar con una persona 👤"
        ))
        return

    respuestas = {
        "ver productos": "🛒 Te paso el catálogo",
        "soporte": "🛠️ Contame tu problema",
        "estado de mi pedido": "📦 Decime tu número de pedido"
    }

    if text in respuestas:
        enviar_Mensaje_whatsapp(text_Message(number, respuestas[text]))
        save_message(number, name, "bot", respuestas[text])
        return

    enviar_Mensaje_whatsapp(text_Message(
        number,
        "No entendí 🤖. Escribí *hola*."
    ))


def replace_start(s):
    return "54" + s[3:] if s.startswith("549") else s
