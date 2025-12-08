import os

# Token de verificación del webhook (el que configuras en Meta)
token = os.getenv("bigdateros")

# Token permanente de WhatsApp API
whatsapp_token = os.getenv("EAAUg1Hjrj6EBQOZAcxz36IJ7sxwvoDHJiwlNR9GW19Lh9N1QDMG7Xep05IUM0WgMF0ExQyZAiDgvskBtOkZBZBh6nXl2SJt75yKE9GH4dIxcTUiRXO6w3VOysS2SRGBplGtBBvrpZByXyVsvNU1CP4P3WcQZBwHdmjpZCi7oZBVcZCsABoZBTC5w9nNRoWIWUY4JLIW04buLtf53L94eINvHQsfPiOvMCvNaeiOoCTsi76zcAGj6qeFuP62s0w9YF39TBD5VpYhRU7aMCHnk0UO0FSfze56gZDZD")

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
