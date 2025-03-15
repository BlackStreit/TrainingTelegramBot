
#Добавить картинки на кнопки
import os
import logging
import asyncio
import aiohttp
import signal
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import traceback

# Загружаем переменные окружения из файла .env
load_dotenv(".env")
TOKEN = os.getenv("BOT_TOKEN")  # Получаем токен бота из переменных окружения
LOGPATH = os.getenv("LOG_PATH")  # Получаем путь к файлу логов из переменных окружения

# Проверяем, что переменные окружения загружены корректно
if not TOKEN:
    raise ValueError("Переменная BOT_TOKEN не найдена в .env файле")
if not LOGPATH:
    raise ValueError("Переменная LOG_PATH не найдена в .env файле")

# Настраиваем логирование для записи событий в файл логов
logging.basicConfig(filename=LOGPATH, level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем объект бота с заданным токеном
bot = Bot(token=TOKEN)
# Создаем объект диспетчера для обработки команд с использованием MemoryStorage
dp = Dispatcher(storage=MemoryStorage())

inline_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Перейти на сайт", url="https://example.com")],
    [InlineKeyboardButton(text="Получить больше информации", callback_data="more_info")]
])

# Функция установки команд бота
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),  # Команда для старта бота
        BotCommand(command="info", description="Вести информацию об авторе"),  # Команда для информации об авторе
        BotCommand(command="random_pic", description="Получить случайную картинку 800 на 600")
    ]
    await bot.set_my_commands(commands)  # Установка списка команд в боте
# Обработчик команды /random_pic - отправляет случайное изображение пользователю
@dp.message(Command("random_pic"))
async def random_pic(message: Message):
    url = "https://picsum.photos/800/600"  # URL для получения случайного изображения
    
    try:
        # Открываем асинхронную HTTP-сессию
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:  # Выполняем GET-запрос с таймаутом
                if response.status == 200:  # Проверяем статус ответа
                    # Отправляем фото пользователю с подписью
                    await message.answer_photo(str(response.url), caption="🎲 Случайное изображение!")
                else:
                    await message.answer("❌ Не удалось загрузить изображение.")
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети: {e}")
        await message.answer("❌ Ошибка сети при получении изображения.")
    except asyncio.TimeoutError:
        logger.error("Таймаут запроса при загрузке изображения.")
        await message.answer("❌ Время ожидания ответа истекло.")
    except Exception as e:
        # Логируем другие ошибки и уведомляем пользователя
        logger.error(f"Неизвестная ошибка загрузки изображения: {e}")
        await message.answer("❌ Произошла неизвестная ошибка при получении изображения.")

# Обработчик команды /start - приветствует пользователя и показывает клавиатуру
@dp.message(Command("start"))
async def start(message: Message):
    text = """*Данные получены!*
_Здравствуйте!_"""  # Сообщение пользователю с использованием Markdown
    await message.answer("Получаю данные...")  # Отправляем сообщение перед выполнением команды
    await asyncio.sleep(1)  # Имитация задержки выполнения
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=inline_kb)  # Отправляем сообщение и показываем клавиатуру

# Обработчик команды /info - отправляет пользователю список доступных команд
@dp.message(Command("info"))
async def info(message: Message):
    text = """<b>Доступные команды:</b>\n
<i>/start</i> - запуск бота\n
<i>/info</i> - получить информацию о командах\n
<i>/random_pic</i> - сгенерировать случайную картинку
"""
    await message.answer(text, parse_mode=ParseMode.HTML)  # Отправляем сообщение в формате HTML

@dp.callback_query(lambda c: c.data == "more_info")
async def process_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer("Вот дополнительная информация!")

async def wait_for_exit(stop_event):
    """Ожидает завершения работы бота через Ctrl+C (для Windows)."""
    try:
        while not stop_event.is_set():
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения, выключаюсь...")
        stop_event.set()

# Основная асинхронная функция для запуска бота с обработкой завершения работы
async def main():
    await set_commands(bot)
    print("Бот запускается...")
    logger.info("Бот включается")  # Логирование запуска
    await dp.start_polling(bot, shutdown_timeout=5)

# Запускаем бота, если скрипт выполняется напрямую
if __name__ == '__main__':
    try:
        asyncio.run(main())  # Запускаем главный цикл бота
    except Exception as e:
        logger.error(f"Ошибка: {e}")  # Логируем ошибку в случае сбоя
        print(f"Ошибка: {e}")  # Выводим ошибку в консоль
		
