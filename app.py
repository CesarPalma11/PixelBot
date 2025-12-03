from flask import Flask, request
import os
import services

app = Flask(__name__)

# Cargar token desde variable de entorno
TOKEN = os.getenv("TOKEN")


@app.route('/bienvenido', methods=['GET'])
def bienvenido():
    return 'Hola mundo!'


@app.route('/webhook', methods=['GET'])
def verificar_token():
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == TOKEN and challenge is not None:
            return challenge
        else:
            return 'token incorrecto', 403

    except Exception as e:
        return str(e), 403


@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']['id']
        messageId = message['id']
        contacts = value['contacts'][0]
        name = contacts['profile']['name']
        text = services.obtener_Mensaje_whatsapp(message)

        services.administrar_chatbot(text, number, messageId, name)

        return 'enviado'

    except Exception as e:
        return 'no enviado: ' + str(e)


if __name__ == '__main__':
    # Para pruebas locales
    app.run(host="0.0.0.0", port=5000)
