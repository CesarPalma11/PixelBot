from flask import Flask, request, jsonify, render_template, redirect, make_response
import requests
from database import init_db, save_message, get_recent_chats, get_chat
import os
from services import administrar_chatbot, obtener_Mensaje_whatsapp, enviar_Mensaje_whatsapp


app = Flask(__name__)
init_db()

# ---------------------------
# CONFIG WHATSAPP API
# ---------------------------
WHATSAPP_TOKEN = "TU_TOKEN_AQUI"
WHATSAPP_PHONE_ID = "TU_PHONE_ID_AQUI"
WHATSAPP_URL = f"https://graph.facebook.com/v17.0/{WHATSAPP_PHONE_ID}/messages"


# ======================================
#   HOME → LISTA DE CHATS DEL DASHBOARD
# ======================================
@app.route("/")
def index():
    chats = get_recent_chats()
    return render_template("index.html", chats=chats)


# ======================================
#   API PARA REFRESCAR LISTA DE CHATS
# ======================================
@app.route("/api/recent_chats")
def api_recent_chats():
    chats = get_recent_chats()
    result = []

    for wa_id, name, timestamp in chats:
        result.append({
            "wa_id": wa_id,
            "name": name,
            "timestamp": timestamp
        })

    response = make_response(jsonify({"chats": result}))
    response.headers["Cache-Control"] = "no-store"  # 🔥 IMPORTANTE
    return response


# ======================================
#   CHAT INDIVIDUAL DEL DASHBOARD
# ======================================
@app.route("/chat/<wa_id>")
def chat_page(wa_id):
    messages = get_chat(wa_id)
    return render_template("chat.html", wa_id=wa_id, messages=messages)


# ======================================
#   API PARA REFRESCAR MENSAJES DEL CHAT
# ======================================
@app.route("/api/chat/<wa_id>/messages")
def api_chat_messages(wa_id):
    data = get_chat(wa_id)

    result = []
    for sender, message, timestamp in data:
        result.append({
            "sender": sender,
            "message": message,
            "timestamp": timestamp
        })

    response = make_response(jsonify({"messages": result}))
    response.headers["Cache-Control"] = "no-store"
    return response


# ======================================
#   ENVIAR MENSAJE DESDE EL DASHBOARD
# ======================================
@app.route("/send_message/<wa_id>", methods=["POST"])
def send_message(wa_id):
    text = request.form.get("text", "")

    if not text:
        return "Missing text", 400

    payload = {
        "messaging_product": "whatsapp",
        "to": wa_id,
        "type": "text",
        "text": {"body": text}
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    requests.post(WHATSAPP_URL, json=payload, headers=headers)

    # Guardar en BD
    save_message(wa_id, "Administrador", "bot", text)

    return "OK", 200


# ======================================
#   WEBHOOK WHATSAPP (RECIBIR MENSAJES)
# ======================================
@app.route("/webhook", methods=["GET", "POST"])
def whatsapp_webhook():

    # ---------------- GET (verificación)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == "pixelbot_token":
            return challenge, 200

        return "Error", 403

    # ---------------- POST (mensaje entrante)
    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages", [])

        if not messages:
            return "No messages", 200

        msg = messages[0]

        wa_id = msg["from"]
        name = value["contacts"][0]["profile"]["name"]
        messageId = msg["id"]

        # ============
        # TEXTO
        # ============
        if msg["type"] == "text":
            text = msg["text"]["body"]

            # Guardar en DB
            save_message(wa_id, name, "usuario", text)

            # Ejecutar BOT
            administrar_chatbot(text, wa_id, messageId, name)

        # ============
        # STICKER
        # ============
        elif msg["type"] == "sticker":
            media_id = msg["sticker"]["id"]

            # Obtener URL del sticker
            media_url = f"https://graph.facebook.com/v17.0/{media_id}"
            headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
            media_response = requests.get(media_url, headers=headers).json()
            dl_url = media_response["url"]

            # Guardamos en DB
            save_message(wa_id, name, "usuario", "[sticker]" + dl_url)

            # Lógica del bot
            administrar_chatbot("[sticker]", wa_id, messageId, name)

    except Exception as e:
        print("ERROR WEBHOOK:", e)

    return "OK", 200

# ======================================
#   RUN
# ======================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
