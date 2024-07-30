import requests
from bs4 import BeautifulSoup
import threading
import time
import schedule
import telebot
from telebot import types
import pickle
import os


url = ['https://tech.wildberries.ru/techschool', 'https://education.tbank.ru/start/']
TOKEN = os.getenv('TG_API_TOKEN')
bot = telebot.TeleBot(TOKEN)
users = []


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(message.chat.id, 'старт ')
    users.append(message.chat.id)
    with open('users.pkl', 'wb') as f:
        pickle.dump(users, f)


def fetch_html(i):
    response = requests.get(url[i])
    return response.text


def parse_wildberries(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    spans = soup.find_all('span')
    return spans


def parse_tbank(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    p_tags = soup.find_all('p')
    corrected_string = []
    i = 0
    while i < len(p_tags):
        try:
            corrected_string.append(p_tags[i].get_text().encode('latin').decode('utf-8'))
            i += 1
        except Exception as e:
            i += 1
    return corrected_string


def tbank(internships):
    html_content = fetch_html(1)
    ps = parse_tbank(html_content)
    total = 0
    for i in range(len(ps)):
        if ps[i] == "Набор открыт":
            internships.append("Появился набор в Т-Банк: " + url[1])
            return internships
        elif ps[i] == "Набор закрыт":
            total += 1
            print(ps[i])
            if total == 12:
                internships.append("T-Bank: все наборы закрыты")
    return internships


def wildberries(internships):
    html_content = fetch_html(0)
    spans = parse_wildberries(html_content)
    total = 0
    for span in spans:
        if span.text == "Набор закрыт":
            total += 1
    if total < 11:
        internships.append("Появился набор в WB: " + url[0])
    else:
        internships.append("WB: все наборы закрыты")


def All_internships():
    internships = []
    wildberries(internships)
    tbank(internships)
    string = ''
    for el in internships:
        string += el + "\n"
    print(string)
    for user in users:
         bot.send_message(user, string)


def foo():
    #schedule.every(5).seconds.do(All_internships) # Для тестов при разработке
    schedule.every().day.at("10:00").do(All_internships)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    if not os.path.isfile('users.pkl'):
        with open('users.pkl', 'wb') as f:
            pickle.dump([], f)

    with open("users.pkl", "rb") as f:
        users = pickle.load(f)
        users = list(set(users))

    thread = threading.Thread(target=foo)
    thread.start()

    bot.polling(none_stop=True)