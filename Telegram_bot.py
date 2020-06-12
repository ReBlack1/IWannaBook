import telebot
from telebot import types
import datetime
import proxy_manager
import BL
import random

proxy = proxy_manager.get_proxy_set().pop()
print(dir(proxy))
print(proxy.is_working)
print(proxy)

proxy_addr = 'https://' + proxy.host + ":" + str(proxy.port)
print(proxy_addr)
telebot.apihelper.proxy = {'https': proxy_addr}
bot = telebot.TeleBot('')
# bot.send_message(489122274, "А можно ведь просто так отправить сообщеньку?")
user_statements = dict()


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # Если нажали на одну из 12 кнопок — выводим гороскоп
    if call.data == "person":
        # Формируем гороскоп
        msg = "вптвотавоватов"
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    # print(message.from_user.id)
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Для поиска книги напиши её описание \r\n"
                                               "Чтоб написать письмо разработчику жми на /support")
        return
    if message.text == "/support":
        user_statements[message.from_user.id] = "support"
        bot.send_message(message.from_user.id, "Введите сообщение для разработчика, он обязательно его получит!")
        return

    if message.text:
        print(user_statements)
        if user_statements.get(message.from_user.id, "") == "support":
            print(message.text)
            user_statements[message.from_user.id] = "book"
            return
        if user_statements.get(message.from_user.id, None) in ["book", None]:
            print("Ищу книгу!")
            BL.find_book_by_desc(message.text)


bot.polling(none_stop=True, interval=0)
