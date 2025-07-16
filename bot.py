from dotenv import load_dotenv
from telethon.sync import TelegramClient
from flask import Flask
import os
import asyncio
import threading
import requests
import time

# ==== Servidor Flask requerido por Render ====
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot funcionando correctamente (Render)'

@app.route('/ping')
def ping():
    return 'pong', 200

def run_web():
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port)

# ==== Funciones del bot ====
async def getListOfGroups(client):
    try:
        dialogs = await client.get_dialogs()
        groups_info = []
        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                entity = await client.get_entity(dialog.id)
                can_send_messages = entity.default_banned_rights is None or not entity.default_banned_rights.send_messages
                if can_send_messages:
                    group_info = {'group_id': dialog.id, 'group_name': dialog.title}
                    groups_info.append(group_info)
        return groups_info
    except Exception as e:
        print(f"Error en getListOfGroups: {e}")
        return []

async def getMessagesFromGroup(client, group_id):
    try:
        all_messages = []
        async for message in client.iter_messages(group_id):
            all_messages.append(message)
        return all_messages
    except Exception as e:
        print(f"Error en getMessagesFromGroup: {e}")
        return []

async def loguserbot():
    load_dotenv()

    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    phone_number = os.getenv("PHONENUMBER")
    session_name = "bot_spammer"

    print(f"API_ID: {api_id}")
    print(f"API_HASH: {api_hash}")
    print(f"Phone Number: {phone_number}")

    if not phone_number:
        print("Error: El número de teléfono no se cargó correctamente desde el archivo .env.")
        return

    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input("Ingrese el código de verificación: "))

    await client.send_message(os.getenv("LOGS_CHANNEL"), "<b>Bot encendido</b>", parse_mode="HTML")
    spammer_group = int(os.getenv("SPAMMER_GROUP"))

    while True:
        groups_info = await getListOfGroups(client)
        messages_list = await getMessagesFromGroup(client, spammer_group)

        try:
            await client.send_message(
                os.getenv("LOGS_CHANNEL"),
                f"<b>CANTIDAD DE MENSAJES CONSEGUIDOS PARA PUBLICAR</b> <code>{len(messages_list)-1}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Error al enviar mensaje de cantidad: {e}")

        try:
            for i in groups_info:
                if i['group_name'] not in ["Peru Sin Limites", "PERU SIN LIMITES"]:
                    j = 0
                    for message_spam in messages_list:
                        j += 1
                        resultado = True
                        try:
                            await client.send_message(i["group_id"], message_spam)
                        except Exception as error:
                            await client.send_message(
                                os.getenv("LOGS_CHANNEL"),
                                f'<b>Mensaje no enviado a {i["group_name"]}</b> - Causa: {error}',
                                parse_mode="HTML"
                            )
                            resultado = False
                        if resultado:
                            await client.send_message(
                                os.getenv("LOGS_CHANNEL"),
                                f'<b>Mensaje enviado a {i["group_name"]}</b>',
                                parse_mode="HTML"
                            )
                            await asyncio.sleep(5)
                        if j == 3:
                            break
                    await client.send_message(os.getenv("LOGS_CHANNEL"), "<b>RONDA ACABADA</b>", parse_mode="HTML")
                    await asyncio.sleep(10)
        except Exception as e:
            print(f"Error en el ciclo principal: {e}")

# ==== Auto-ping para mantener activo Render ====
def auto_ping():
    while True:
        try:
            url = os.getenv("SELF_URL", "https://telegram-spam-bot2.onrender.com/")
            print(f"Auto-ping to {url}")
            requests.get(url)
        except Exception as e:
            print(f"Error en autoping: {e}")
        time.sleep(300)  # cada 5 minutos

# ==== Iniciar bot ====
def start_bot():
    try:
        asyncio.run(loguserbot())
    except Exception as e:
        print(f"Error crítico en loguserbot: {e}")

# ==== Ejecución principal ====
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    threading.Thread(target=start_bot, daemon=True).start()
    threading.Thread(target=auto_ping, daemon=True).start()

    while True:
        time.sleep(1)
