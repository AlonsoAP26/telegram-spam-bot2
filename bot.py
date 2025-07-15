from dotenv import load_dotenv
from telethon.sync import TelegramClient, events
import os
import asyncio

# Obtener lista80 de grupos
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
                    groups_info.append(group_info)  # Asegúrate de agregar el grupo a la lista
        return groups_info
    except Exception as e:
        print(f"Error en getListOfGroups: {e}")
        return []

# Obtener mensajes de un grupo específico
async def getMessagesFromGroup(client, group_id):
    try:
        all_messages = []
        async for message in client.iter_messages(group_id):  # Usar iter_messages en lugar de inter_messages
            all_messages.append(message)
        return all_messages
    except Exception as e:
        print(f"Error en getMessagesFromGroup: {e}")
        return []

# Función principal para el bot
async def loguserbot():
    load_dotenv()

    # Cargar las variables de entorno
    api_id = int(os.getenv("API_ID"))
    api_hash = os.getenv("API_HASH")
    phone_number = os.getenv("PHONENUMBER")
    session_name = "bot_spammer"

    # Depurar las variables para asegurarnos de que están siendo cargadas correctamente
    print(f"API_ID: {api_id}")
    print(f"API_HASH: {api_hash}")
    print(f"Phone Number: {phone_number}")  # Aquí verificamos si el número se carga correctamente

    if not phone_number:
        print("Error: El número de teléfono no se cargó correctamente desde el archivo .env.")
        return

    client = TelegramClient(session_name, api_id, api_hash)

    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        await client.sign_in(phone_number, input('Ingrese el código de verificación: '))

    await client.send_message(os.getenv("LOGS_CHANNEL"), f'<b>Bot encendido</b>', parse_mode="HTML")
    spammer_group = int(os.getenv('SPAMMER_GROUP'))

    while True:  # Cambiado 'true' por 'True'
        groups_info = await getListOfGroups(client)
        messages_list = await getMessagesFromGroup(client, spammer_group)

        try:
            await client.send_message(os.getenv("LOGS_CHANNEL"), f"<b>CANTIDAD DE MENSAJES CONSEGUIDOS PARA PUBLICAR</b> <code>{len(messages_list)-1}</code>", parse_mode="HTML")
        except Exception as e:
            print(f"Error al enviar mensaje de cantidad: {e}")
            pass

        try:
            for i in groups_info:
                if i['group_name'] not in ["PeruSinLimites", "PERU SIN LIMITES"]:  # Asegúrate de que el nombre sea correcto
                    j = 0
                    for message_spam in messages_list:
                        j += 1
                        resultado = True  # Cambiado 'resultado = true' a 'True'
                        try:
                            await client.send_message(i["group_id"], message_spam)
                        except Exception as error:
                            await client.send_message(os.getenv("LOGS_CHANNEL"), f'<b>Mensaje no enviado a {i["group_name"]}</b> - Causa: {error}', parse_mode="HTML")
                            resultado = False
                        if resultado:
                            await client.send_message(os.getenv("LOGS_CHANNEL"), f'<b>Mensaje enviado a {i["group_name"]}</b>', parse_mode="HTML")
                            await asyncio.sleep(11)
                        if j == 3:  # Se limita a 3 mensajes por grupo
                            break
                    await client.send_message(os.getenv("LOGS_CHANNEL"), f'<b>RONDA ACABADA</b>', parse_mode="HTML")
                    await asyncio.sleep(10)
        except Exception as e:
            print(f"Error en el ciclo principal: {e}")
            pass

if __name__ == "__main__":
    asyncio.run(loguserbot())  # Corregido la indentación aquí también
