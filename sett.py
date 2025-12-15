import os

# Token de verificación del webhook (el que configuras en Meta)
token = os.getenv("bigdateros")

# Token permanente de WhatsApp API
whatsapp_token = os.getenv("EAAUg1Hjrj6EBQJnuaEum23rMlJJBl8U5OnP8rwI6L2rbyZCOQsCaNeHz0bSvOVsZA8rZAlyscaYKZCJvp7N8CDiUcgJNcIZBhub0EiWDOmIZC3IOZBMDGDhz2qSXpZBRYZBmYzCqoegokIuP631V0FwNss6QTv4CEZAXWyQFWQa0DZBOdgOjTofS6YBVcwNTNlEJQrGvyCvv5q7gmI3GkaMZAQI9hvYqTTVbPpfLXCeSz0zN99oLtZBO3VcKim9IC85eRfaUg3W3waEClGRAS7onPTuKe1NgD")

# Phone Number ID
PHONE_NUMBER_ID = os.getenv("876431475556153")

# URL final que usa el bot para enviar mensajes
whatsapp_url = f"https://graph.facebook.com/v22.0/{876431475556153}/messages"

# URL de un documento de prueba
document_url = os.getenv("DOCUMENT_URL")

# Stickers u otros medios
stickers = {
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
