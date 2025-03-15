import os
import asyncio
import logging
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.enums.parse_mode import ParseMode

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOG_PATH = os.getenv("LOG_PATH")

# Настройки OpenAI API
API_URL = "https://api.openai.com/v1/chat/completions"
WHISPER_API_URL = "https://api.openai.com/v1/audio/transcriptions"
SYSTEM_PROMPT = "Ты умный Telegram-бот, который помогает людям отвечать на вопросы."

# Настройки бота
logging.basicConfig(level=logging.INFO, filename= LOG_PATH)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище контекста диалогов пользователей
user_contexts = {}

async def transcribe_voice(voice_file: bytes):
    """Отправляет голосовое сообщение в OpenAI Whisper для транскрибации."""
    files = {"file": ("audio.ogg", voice_file, "audio/ogg")}
    data = {"model": "whisper-1"}
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(WHISPER_API_URL, headers=headers, data=data, files=files)
            response.raise_for_status()
            transcription = response.json()["text"]
            logger.info(f"Транскрибация выполнена: {transcription}")
            return transcription
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка API Whisper: {e.response.text}")
        return "Ошибка при распознавании аудио. Попробуйте позже."
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return "Произошла непредвиденная ошибка. Попробуйте позже."

async def ask_chatgpt(user_id: int, message: str):
    """Отправляет сообщение в OpenAI API и возвращает ответ."""
    logger.info(f"Пользователь {user_id} отправил сообщение: {message}")
    context = user_contexts.get(user_id, [])
    context.append({"role": "user", "content": message})
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + context,
        "max_tokens": 400
    }
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            reply = response.json()["choices"][0]["message"]["content"]
            context.append({"role": "assistant", "content": reply})
            user_contexts[user_id] = context[-10:]  # Ограничиваем длину контекста
            logger.info(f"Ответ от ChatGPT для пользователя {user_id}: {reply}")
            return reply
    except httpx.HTTPStatusError as e:
        logger.error(f"Ошибка API OpenAI: {e.response.text}")
        return "Ошибка при обращении к ChatGPT. Попробуйте позже."
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        return "Произошла непредвиденная ошибка. Попробуйте позже."


@dp.message(CommandStart())
async def start_command(message: Message):
    """Обрабатывает команду /start."""
    logger.info(f"Пользователь {message.from_user.id} запустил бота.")
    await message.answer("Привет! Отправь мне сообщение, и я отвечу с помощью ChatGPT.")

@dp.message(lambda message: message.voice)
async def handle_voice_message(message: Message):
    """Обрабатывает голосовые сообщения."""
    user_id = message.from_user.id
    file_id = message.voice.file_id
    voice_file = await bot.download(file_id)
    voice_bytes = voice_file.getvalue()
    
    logger.info(f"Пользователь {user_id} отправил голосовое сообщение.")
    await message.answer("🎙 Распознаю голосовое сообщение...")
    transcribed_text = await transcribe_voice(voice_bytes)
    if transcribed_text.startswith("Ошибка"):
        await message.answer(transcribed_text)
        return
    
    await message.answer(f"✍️ Распознанный текст: {transcribed_text}", parse_mode="HTML")
    response = await ask_chatgpt(user_id, transcribed_text)
    await message.answer(response, parse_mode=ParseMode.MARKDOWN)

@dp.message()
async def handle_message(message: Message):
    """Обрабатывает входящие сообщения."""
    user_id = message.from_user.id
    text = message.text.strip()
    
    if not text:
        logger.warning(f"Пользователь {user_id} отправил пустое сообщение.")
        await message.answer("Пожалуйста, отправьте текстовое сообщение.")
        return
    
    logger.info(f"Пользователь {user_id} отправил сообщение: {text}")
    await message.answer("⏳ Думаю...")
    response = await ask_chatgpt(user_id, text)
    await message.answer(response)




async def main():
    """Запуск бота."""
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())