import requests  # Импортируем библиотеку для отправки HTTP-запросов
from bs4 import BeautifulSoup  # Импортируем BeautifulSoup для парсинга HTML
import threading
import time
import schedule
import telebot
from telebot import types
import pickle
import os

# Ваш токен для Telegram-бота
TOKEN = os.getenv('TG_API_TOKEN')
bot = telebot.TeleBot(TOKEN)
users = []

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(message.chat.id, 'старт ')
    users.append(message.chat.id)
    with open('users.pkl', 'wb') as f:
        pickle.dump(users, f)

# URL страницы, которую будем парсить
url = 'https://tech.wildberries.ru/techschool'


def fetch_html():
    response = requests.get(url)  # Отправляем запрос и получаем ответ
    return response.text  # Получаем HTML-код страницы в виде строки


def parse_courses(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')  # Создаём объект для парсинга
    spans = soup.find_all('span')  # Ищем все теги <span>
    return spans


def course():
    html_content = fetch_html()
    spans = parse_courses(html_content)
    total = 0
    for span in spans:
        if span.text == "Набор закрыт":
            total += 1
    if total < 11:
        for user in users:
            bot.send_message(user, "Есть курс")  # Отправляем сообщение в Telegram
    else:
        for user in users:
            bot.send_message(user, "Курса нет")  # Отправляем сообщение в Telegram


def foo():
    schedule.every().day.at("10:00").do(course)    # Запускать функцию каждый час
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    #CHAT_ID = '389769794' '433677155'
    if not os.path.isfile('users.pkl'):
        with open('users.pkl', 'wb') as f:
            pickle.dump([], f)

    with open("users.pkl", "rb") as f:
        users = pickle.load(f)
    # Создаем и запускаем поток для планировщика
    thread = threading.Thread(target=foo)
    thread.start()

    # Запускаем бота
    bot.polling(none_stop=True)
