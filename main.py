import threading
import time
import schedule
import telebot
from telebot import types
import pickle
import os
import logging
from functions import All_internships

logger = logging.getLogger(__name__)
TOKEN = os.getenv('TG_API_TOKEN')
bot = telebot.TeleBot(TOKEN)
users = set()


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.send_message(message.chat.id,
                     'В данном боте вы можете узнать об открытых наборах на стажировки в различных компаниях')
    users.add(message.chat.id)
    send_main_menu(message.chat.id)
    with open('users.pkl', 'wb') as f:
        pickle.dump(users, f)


@bot.message_handler(commands=['menu'])
def menu(message: types.Message):
    send_main_menu(message.chat.id)

@bot.message_handler(commands=['notifications'])
def menu(message: types.Message):
    send_notification_menu(message.chat.id)


############################## МЕНЮ ########################################

def send_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    button_notifications = types.InlineKeyboardButton("Уведомления", callback_data="notifications")
    markup.add(button_notifications)
    bot.send_message(chat_id, "Выберите действие из меню:", reply_markup=markup)


def send_notification_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    button_on_off = types.InlineKeyboardButton("Вкл/Выкл", callback_data="on_off")
    button_back = types.InlineKeyboardButton("Назад", callback_data="back")
    markup.add(button_on_off, button_back)
    bot.send_message(chat_id, "Включить/выключить уведомления от бота", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["notifications", "on_off", "back"])
def handle_callback(call):
    chat_id = call.message.chat.id

    if call.data == "notifications":
        send_notification_menu(chat_id)
    elif call.data == "on_off":
        if chat_id in users:
            bot.send_message(chat_id, "Уведомления выключены")
            users.remove(chat_id)
            with open('users.pkl', 'wb') as f:
                pickle.dump(users, f)
        else:
            bot.send_message(chat_id, "Уведомления включены")
            users.add(chat_id)
            with open('users.pkl', 'wb') as f:
                pickle.dump(users, f)
        send_notification_menu(chat_id)
    elif call.data == "back":
        send_main_menu(chat_id)


def notifications_for_users():
    string = All_internships()
    for user in users:
        bot.send_message(user, string)
    logger.info("Notifications sent to users")


def message_scheduler():
    #schedule.every(5).seconds.do(notifications_for_users)
    schedule.every().day.at("10:00").do(notifications_for_users)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    if not os.path.isfile('users.pkl'):
        with open('users.pkl', 'wb') as f:
            pickle.dump(set(), f)

    with open("users.pkl", "rb") as f:
        users = pickle.load(f)

    thread = threading.Thread(target=message_scheduler)
    thread.start()

    while True:
        try:
            bot.polling(none_stop=True, timeout=40)

        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(15)
