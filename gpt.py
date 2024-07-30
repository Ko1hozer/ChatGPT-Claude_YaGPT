from flask import Flask, request, jsonify
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

app = Flask(name)

# Ваши API ключи
CHATGPT_API_KEY = 'your_openai_api_key'
CLAUDE_API_KEY = 'your_claude_api_key'
YANDEXGPT_API_KEY = 'your_yandexgpt_api_key'
TELEGRAM_TOKEN = 'your_telegram_bot_token'

def chatgpt_response(prompt):
    headers = {
        'Authorization': f'Bearer {CHATGPT_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': prompt}],
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

def claude_response(prompt):
    headers = {
        'Authorization': f'Bearer {CLAUDE_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'prompt': prompt,
        'max_tokens': 150
    }
    response = requests.post('https://api.anthropic.com/v1/claude/completions', headers=headers, json=data)
    return response.json()['completion']

def yandexgpt_response(prompt):
    headers = {
        'Authorization': f'Bearer {YANDEXGPT_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': prompt}],
    }
    response = requests.post('https://api.yandex.com/gpt/v1/chat/completions', headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я ваш AI-ассистент. Как я могу помочь?')

def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    
    # Выбор модели (можно сделать более сложным в зависимости от команды пользователя)
    ai_choice = "chatgpt"  # Здесь можно добавить логику выбора ИИ на основе запроса
    
    if ai_choice == "chatgpt":
        answer = chatgpt_response(user_message)
    elif ai_choice == "claude":
        answer = claude_response(user_message)
    elif ai_choice == "yandexgpt":
        answer = yandexgpt_response(user_message)

    update.message.reply_text(answer)

def run_telegram_bot():
    updater = Updater(TELEGRAM_TOKEN)
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    updater.idle()

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    user_message = req['request']['original_utterance']
    
    # Выбор модели (можно сделать более сложным в зависимости от команды пользователя)
    ai_choice = "chatgpt"  # Здесь можно добавить логику выбора ИИ на основе запроса
    
    if ai_choice == "chatgpt":
        answer = chatgpt_response(user_message)
    elif ai_choice == "claude":
        answer = claude_response(user_message)
    elif ai_choice == "yandexgpt":
        answer = yandexgpt_response(user_message)

    response_text = {
        "response": {
            "text": answer,
            "tts": answer,
            "buttons": [],
            "end_session": False
        },
        "session": req['session'],
        "version": req['version']
    }
    
    return jsonify(response_text)

if name == 'main':
    # Запуск Telegram-бота в отдельном потоке
    from threading import Thread
    telegram_thread = Thread(target=run_telegram_bot)
    telegram_thread.start()

    app.run(port=5000)
