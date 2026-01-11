import os
import json
import requests
from database import save_message, set_handoff, is_handoff

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"


# ======================
# MEMORIA TEMPORAL
# ======================
_reaccionados = {}

def ya_reacciono(number):
    return _reaccionados.get(number, False)

def set_reacciono_flag(number):
    _reaccionados[number] = True


# ======================
# WHATSAPP API
# ======================
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


def buttonReply_Message(number, body):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "chatbots", "title": "🤖 Chatbots"}},
                    {"type": "reply", "reply": {"id": "webs", "title": "🌐 Páginas web"}},
                    {"type": "reply", "reply": {"id": "asesor", "title": "💼 Asesor"}}
                ]
            }
        }
    })


def obtener_Mensaje_whatsapp(msg):
    if msg["type"] == "text":
        return msg["text"]["body"], None
    if msg["type"] == "interactive":
        reply = msg["interactive"]["button_reply"]
        return reply["title"], reply["id"]
    return "", None


def marcar_como_leido(message_id):
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    requests.post(WHATSAPP_URL, json=payload, headers=headers)


def reaccionar_mensaje(message_id, emoji="👋"):
    payload = {
        "messaging_product": "whatsapp",
        "type": "reaction",
        "reaction": {
            "message_id": message_id,
            "emoji": emoji
        }
    }
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    requests.post(WHATSAPP_URL, json=payload, headers=headers)


# ======================
# BOT LOGIC (FIXED)
# ======================
def administrar_chatbot(text, intent, number, messageId, name):
    text = (text or "").lower().strip()

    if is_handoff(number):
        return

    marcar_como_leido(messageId)

    # ---- SALUDO ----
    if "hola" in text:
        if not ya_reacciono(number):
            reaccionar_mensaje(messageId, "👋")
            set_reacciono_flag(number)

        msg = "👋 ¡Hola! Soy PixelBot. ¿Cómo podemos ayudarte?"

        enviar_Mensaje_whatsapp(
            buttonReply_Message(number, msg)
        )

        save_message(number, name, "bot", msg)
        return

    # ---- CHATBOTS ----
    if intent == "chatbots":
        msg = (
            "🚀 Automatizamos WhatsApp para tu negocio.\n\n"
            "✔️ Bots 24/7\n"
            "✔️ Ventas automáticas\n"
            "✔️ Atención híbrida\n\n"
            "¿Querés una demo?"
        )

        enviar_Mensaje_whatsapp(text_Message(number, msg))
        save_message(number, name, "bot", msg)
        return

    # ---- WEBS ----
    if intent == "webs":
        msg = (
            "🌐 Diseñamos páginas web modernas y rápidas.\n\n"
            "✔️ Landing pages\n"
            "✔️ Webs corporativas\n"
            "✔️ Integración con WhatsApp"
        )

        enviar_Mensaje_whatsapp(text_Message(number, msg))
        save_message(number, name, "bot", msg)
        return

    # ---- ASESOR ----
    if intent == "asesor" or text == "asesor":
        set_handoff(number, minutes=60)

        msg = (
            "👤 Te paso con un asesor de PixelTech.\n"
            "⏱️ A la brevedad se comunicarán con usted."
        )

        enviar_Mensaje_whatsapp(text_Message(number, msg))
        save_message(number, name, "bot", msg)
        return


def replace_start(s):
    return "54" + s[3:] if s.startswith("549") else s
