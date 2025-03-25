import asyncio
from datetime import datetime
from pyrogram import Client
from pyrogram.errors.exceptions.forbidden_403 import Forbidden
from pyrogram.errors.exceptions.flood_420 import SlowmodeWait
from loguru import logger
from generate import create_request
from pyrogram.enums import ChatMemberStatus
from config import API_ID, API_HASH, APP_NAME
import time

app = Client(APP_NAME, api_id=API_ID, api_hash=API_HASH)



with open('channels.txt', 'r') as file:
    channels_to_track = [line.strip() for line in file if line.strip()]

last_messages = {channel: [] for channel in channels_to_track}


logger.add("logfile.log", rotation="1 MB", level="INFO", format="{time} {level} {message}")



async def is_subscribed(client, channel):
    logger.info(f"Проверка статуса подписки на канал: {channel}")
    try:
        member = await client.get_chat_member(channel, 'me')
        logger.info(f"Статус подписки на канал {channel}: {member.status}")
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]
    except Exception as e:
        logger.error(f'Не удалось проверить статус подписки на {channel}: {e}')
        return False

async def handle_message(client, message):
    if message.from_user is None and message.sender_chat is None:
        logger.info(f"Пропускаем рекламное сообщение: {message.message_id}")
        return
    
    if message.text:  
        context = message.text
    elif message.caption:  
        context = message.caption
    else:
        logger.info(f"Пропускаем сообщение без текста")
        return 
    
    await asyncio.sleep(2)  # Задержка перед получением обсуждения
    logger.info(f"Получаем обсуждение для сообщения: {message.id} в канале {message.chat.title}")

    dm = await client.get_discussion_message(message.chat.id, message.id)
    message_text = await create_request(context)
    await asyncio.sleep(3)  

    logger.info(f"Отправка сообщения: '{message_text}' в обсуждение канала {message.chat.title}")
    try:
        await dm.reply(message_text)
        time.sleep(5) 
    except Forbidden:
        logger.warning(f"Нет доступа к обсуждению канала {message.chat.title}. Присоединяемся к чату.")
        await dm.chat.join()
        await dm.reply(message_text)
    except SlowmodeWait as e:
        logger.warning(f"Достигнут режим замедления. Ошибка: {e}. Пропускаем сообщение.")
        return

async def check_new_messages(channel):
    global last_messages
    try:
        messages = app.get_chat_history(channel, limit=2)

        messages_list = []
        async for message in messages:
            messages_list.append(message)

        if len(messages_list) < 2:
            logger.info(f"В канале {channel} недостаточно сообщений для обработки.")
            last_messages[channel] = messages_list
            return

        first_message = messages_list[0]
        new_message = False
        if len(last_messages[channel]) == 0:
            last_messages[channel] = messages_list
            return

        if first_message.id != last_messages[channel][0].id:
            new_message = True

        if new_message:
            logger.info(f"Новое сообщение в канале {channel}: {first_message.text}")
            asyncio.create_task(handle_message(app, first_message))

            last_messages[channel] = messages_list
    except Exception as e:
        logger.error(f"Ошибка при проверке новых сообщений в канале {channel}: {e}")

async def main():
    async with app:
        for channel in channels_to_track:
            if not await is_subscribed(app, channel):
                try:
                    await asyncio.sleep(5)  
                    await app.join_chat(channel)
                    logger.info(f'Успешно присоединились к каналу: {channel}')
                    time.sleep(5) 
                except Exception as e:
                    logger.error(f'Не удалось присоединиться к каналу {channel}: {e}')

        while True:
            tasks = []
            for channel in channels_to_track:
                tasks.append(asyncio.create_task(check_new_messages(channel)))
            
            await asyncio.gather(*tasks)
            await asyncio.sleep(6) 

if __name__ == "__main__":
    logger.info(f'Приложение успешно запущено {datetime.now()}')
    app.run(main())