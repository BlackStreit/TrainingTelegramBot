# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 18:56:04 2025

@author: Admin
"""

"""
#### **Задание 2: Бот с командами `/start` и `/help`**  
**Цель:** Освоить обработку команд и научиться отправлять текстовые сообщения пользователю.  

✅ **Ожидаемый результат:**  
- При вводе `/start` бот отправляет приветственное сообщение  
- При вводе `/help` бот отправляет список доступных команд  

"""

import os
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from datetime import datetime



load_dotenv(".env")
TOKEN = os.getenv("BOT_TOKEN")
LOGPATH = os.getenv("LOG_PATH")

if not TOKEN or not LOGPATH:
	raise ValueError("Заполните env файл")

logging.basicConfig(filename=LOGPATH, level = logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def start(message: Message):
	text = "*Данные получены!*\n_Здравствуйте!_"
	await message.answer("Получаю данные...")
	await asyncio.sleep(1)
	await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("info"))
async def info(message: Message):
	text = """<b>Доступные команды:</b>\n
<i>/start</i> - запуск бота\n
<i>/info</i> - получить информацию о командах
"""

	await message.answer(text, parse_mode=ParseMode.HTML)

async def main():
	await dp.start_polling(bot)

if __name__ == '__main__':
	try:
		import nest_asyncio
		nest_asyncio.apply()
		asyncio.run(main())

	except Exception as e:
		logger.error(e)
		print(e)