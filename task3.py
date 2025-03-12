import os
import logging
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv(".env")
TOKEN = os.getenv("BOT_TOKEN")  # Токен бота
LOGPATH = os.getenv("LOG_PATH")  # Путь к файлу логов

# Проверяем, что переменные окружения загружены
if not TOKEN:
    raise ValueError("Переменная BOT_TOKEN не найдена в .env файле")
if not LOGPATH:
    raise ValueError("Переменная LOG_PATH не найдена в .env файле")

# Настраиваем логирование
logging.basicConfig(filename=LOGPATH, level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем объект бота с указанным токеном и форматом сообщений HTML
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
# Создаем объект диспетчера для обработки команд
dp = Dispatcher()

# Обработчик команды /random_pic - отправка случайного изображения
@dp.message(Command("random_pic"))
async def random_pic(message: Message):
    url = "https://picsum.photos/800/600"  # URL для получения случайного изображения
    
    try:
        # Открываем асинхронную сессию HTTP-запросов
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:  # Отправляем GET-запрос
                if response.status == 200:  # Проверяем статус ответа
                    # Отправляем фото пользователю, преобразовав URL в строку
                    await message.answer_photo(str(response.url), caption="🎲 Случайное изображение!")
                else:
                    await message.answer("❌ Не удалось загрузить изображение.")
    except Exception as e:
        # Логируем ошибку и уведомляем пользователя
        logger.error(f"Ошибка загрузки изображения: {e}")
        await message.answer("❌ Произошла ошибка при получении изображения.")

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)  # Запускаем бота в режиме опроса обновлений

# Запуск бота
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        print(f"Ошибка: {e}")
