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
    text_raw = text
    text = text.lower().strip()

    print("🤖 BOT RECIBE:", text, "handoff:", is_handoff(number))

    # 👤 salida manual de humano
    if text in ["bot", "activar bot", "volver al bot"]:
        from database import disable_handoff
        disable_handoff(number)

        enviar_Mensaje_whatsapp(text_Message(
            number,
            "🤖 El bot de PixelTech volvió a activarse.\nEscribí *hola* para continuar."
        ))
        save_message(number, name, "bot", "🤖 Bot reactivado")
        return

    # 🔒 bloqueo SOLO si está en humano
    if is_handoff(number):
        print("🔴 Modo humano activo — bot en pausa")
        return

    # 👤 asesor
    if text in ["asesor", "hablar con un asesor", "persona", "humano"]:
        set_handoff(number, minutes=60)
        enviar_Mensaje_whatsapp(text_Message(
            number,
            "👤 Te asignamos un asesor de *PixelTech*.\n"
            "⏱️ Atención humana durante 1 hora."
        ))
        save_message(number, name, "bot", "👤 Atención humana activada")
        return

    # 👋 saludo
    if text.startswith("hola") or text.startswith("buen"):
        enviar_Mensaje_whatsapp(buttonReply_Message(
            number,
            [
                "🤖 Chatbots para WhatsApp",
                "🌐 Páginas web profesionales",
                "💼 Hablar con un asesor"
            ],
            "👋 Hola, somos *PixelTech*\n"
            "Desarrollamos chatbots inteligentes y páginas web modernas.\n\n"
            "¿Qué te gustaría conocer?"
        ))
        save_message(number, name, "bot", "👋 Menú principal")
        return

    respuestas = {
        "🤖 chatbots para whatsapp":
            "🚀 Automatizamos ventas y atención en WhatsApp.\n\n"
            "✔️ Bots 24/7\n"
            "✔️ Integración con CRM\n"
            "✔️ Handoff humano\n"
            "✔️ Métricas en tiempo real\n\n"
            "¿Querés una demo?",

        "🌐 páginas web profesionales":
            "🎨 Diseñamos webs rápidas y modernas.\n\n"
            "✔️ Landing pages\n"
            "✔️ Webs corporativas\n"
            "✔️ SEO + WhatsApp\n\n"
            "¿Para qué tipo de negocio?",

        "💼 hablar con un asesor":
            "Perfecto 👍 escribí *asesor* y te atendemos."
    }

    if text in respuestas:
        enviar_Mensaje_whatsapp(text_Message(number, respuestas[text]))
        save_message(number, name, "bot", respuestas[text])
        return

    enviar_Mensaje_whatsapp(text_Message(
        number,
        "🤖 No entendí tu mensaje.\n"
        "Escribí *hola* para ver las opciones."
    ))


def replace_start(s):
    return "54" + s[3:] if s.startswith("549") else s
