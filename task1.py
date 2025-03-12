# -*- coding: utf-8 -*-
"""
Задание 1: Простейший эхо-бот
Цель: Разобраться с основами работы aiogram и создать бот, 
который повторяет отправленные пользователем сообщения.
"""

import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
LOGSPATH =  os.getenv("LOG_PATH")

if not TOKEN or not LOGSPATH:
	raise ValueError("Заполните .env файл!")

logging.basicConfig(filename=LOGSPATH, level = logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"{datetime.now()} Бот запущен")

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def answer(message: Message):
	text = message.text.strip()
	
	if not text:
		print("Пустое сообщение от {message.from_user.id}")
		logger.warn(f"{datetime.now()} Пустое сообщение от {message.from_user.id}")
		await message.reply("Пусто")
	
	await message.reply(text)

async def main():
	print("Бот запускатеся")
	logger.info(f"{datetime.now()} Бот запущен")
	await dp.start_polling(bot)

if __name__ == '__main__':
	try:
		asyncio.run(main())
	except Exception as ex:
		logger.info(f"{datetime.now()} Ошибка {ex}")
