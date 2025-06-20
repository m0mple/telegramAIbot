from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
user_contexts = {}

# Обработчик команды start
@dp.message(Command("start"))
async def command_start(message: Message):
    user_id = message.from_user.id
    user_contexts[user_id] = []
    await message.answer("Привет! Я бот, который готов ответить на любой твой вопрос. Напиши что-нибудь!")

# Обработчик команды help
@dp.message(Command("help"))
async def command_help(message: Message):
    await message.answer("Просто напиши мне любое сообщение.")

# Обработчик текстовых сообщений
@dp.message()
async def handle_message(message: Message):
    user_id = message.from_user.id
    user_message = message.text

    # Добавляем сообщение пользователя в контекст
    if user_id not in user_contexts:
        user_contexts[user_id] = []
    user_contexts[user_id].append({"role": "user", "content": user_message})

    # Отправляем запрос в LLM
    await message.answer("Ещё чуть чуть...")
    llm_response = await send_to_llm(user_contexts[user_id])

    # Добавляем ответ ИИ в контекст
    user_contexts[user_id].append({"role": "assistant", "content": llm_response})

    # Отправляем ответ пользователю с указанием на использование стороннего сервиса
    await message.answer(
        llm_response,
        parse_mode=ParseMode.HTML,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Powered by DeepSeek",
                        url="https://openrouter.ai/deepseek/deepseek-r1-0528-qwen3-8b:free/api"
                    )
                ]
            ]
        )
    )

# Функция для отправки запросов к LLM через OpenRouter API
async def send_to_llm(messages):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://t.me/@m0mple_bot",
        "X-Title": "Telegram Bot"  # Название приложения
    }

    # Формируем запрос для LLM
    data = {
        "model": "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "messages": messages
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()

        # Проверяем наличие ключа 'choices' в ответе
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return "Произошла ошибка при обработке ответа от API. Попробуйте ещё раз."
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

# Запуск бота
if __name__ == '__main__':
    dp.run_polling(bot, skip_updates=True)