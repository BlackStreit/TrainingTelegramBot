import os
import logging
import asyncio
import aiohttp
import signal
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
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

# Создаем кнопки для клавиатуры
button_start = KeyboardButton(text="/start")  # Кнопка для команды /start
button_info = KeyboardButton(text="/info")  # Кнопка для команды /info
button_pic = KeyboardButton(text="/random_pic")  # Кнопка для команды /random_pic

# Создаем объект клавиатуры с кнопками
keyBoard = ReplyKeyboardMarkup(
    keyboard=[[button_start, button_info], [button_pic]],  # Располагаем кнопки в строках
    one_time_keyboard=False  # Клавиатура остается на экране после использования
)

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
    await message.answer(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyBoard)  # Отправляем сообщение и показываем клавиатуру

# Обработчик команды /info - отправляет пользователю список доступных команд
@dp.message(Command("info"))
async def info(message: Message):
    text = """<b>Доступные команды:</b>\n
<i>/start</i> - запуск бота\n
<i>/info</i> - получить информацию о командах\n
<i>/random_pic</i> - сгенерировать случайную картинку
"""
    await message.answer(text, parse_mode=ParseMode.HTML)  # Отправляем сообщение в формате HTML

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
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    
    def shutdown():
        logger.info("Получен сигнал завершения, выключаюсь...")
        stop_event.set()
    
    if os.name != "nt":  # Только для Unix-систем
        loop.add_signal_handler(signal.SIGTERM, shutdown)
        loop.add_signal_handler(signal.SIGINT, shutdown)
    else:  # Windows: используем альтернативный способ завершения
        asyncio.create_task(wait_for_exit(stop_event))

    
    await dp.start_polling(bot, stop_event=stop_event)

# Запускаем бота, если скрипт выполняется напрямую
if __name__ == '__main__':
    try:
        asyncio.run(main())  # Запускаем главный цикл бота
    except Exception as e:
        logger.error(f"Ошибка: {traceback.format_exc()}")  # Логируем ошибку в случае сбоя
        print(f"Ошибка: {traceback.format_exc()}")  # Выводим ошибку в консоль
		
