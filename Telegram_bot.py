import telebot
import pickle
import tokenizer
import pymorphy2
import client
from scipy.spatial.distance import cosine
from config import token

# proxy =  "5.44.45.207:45785" "#  proxy_manager.get_proxy_set().pop()

# proxy_addr = 'https://SelReBlack1:K1g1GfI@5.44.45.207:45785'  # + proxy.host + ":" + str(proxy.port)
# telebot.apihelper.proxy = {'https': proxy_addr}
bot = telebot.TeleBot(token)

user_statements = dict()

def log(text):
    pass

def add_filter_for_user(rt):
    pass

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # Если нажали на одну из 12 кнопок — выводим гороскоп
    if call.data == "person":
        # Формируем гороскоп
        msg = "вптвотавоватов"
        # Отправляем текст в Телеграм
        bot.send_message(call.message.chat.id, msg)

morph = pymorphy2.MorphAnalyzer()
with open(r"person_train.plc", 'rb') as f:
    person_clf = pickle.load(f)
with open(r"do_train", 'rb') as f:
    do_clf = pickle.load(f)
with open("catalog.plc", 'rb') as f:
    catalog = pickle.load(f)
print(len(catalog))
print("Каталог загружен")


def make_ans(recom_list):
    ans = "Предлагаю вам что-нибудь такое: \r\n\r\n"
    for i in range(len(recom_list)):
        if recom_list[i][1]:
            ans += str(i+1) + ". " + recom_list[i][1] + " // " + recom_list[i][0] + ", Оценка " + str(recom_list[i][2])[:4] + "\r\n\r\n"
    return ans



def get_recommendation(parsed_req):
    rec_list = [(None,None,0), (None,None,0), (None,None,0)]
    for book_num in catalog:
        access_list = []
        for req_key in parsed_req:
            if catalog[book_num][2].get(req_key, None) is None or len(catalog[book_num][2][req_key]) == 0:
                continue
            key_access_list = []
            for req_vec in parsed_req[req_key]:
                key_access_list.append(1 - cosine(catalog[book_num][2][req_key], req_vec))
            key_access = max(key_access_list)
            if req_key == "persons_vec":
                key_access *= 1
            elif req_key in ["state_vec", "do_vec"]:
                key_access *= 1
            access_list.append(key_access)
        if not access_list:
            continue
        access = sum(access_list)
        for i in range(len(rec_list)):
            if rec_list[i][2] < access:
                rec_list.insert(i, (catalog[book_num][0], catalog[book_num][1], access))
                rec_list = rec_list[:3]
                break
    print("Рекомендация", rec_list)
    return make_ans(rec_list)


def find_book(req_text):
    print("НОВЫЙ ЗАПРОС: ", req_text)
    text = req_text.split()
    parsed_req = dict()
    for word in text:
        token_word = tokenizer.get_stat_token_word(morph, word)
        if token_word is None:
            continue
        vec = client.get_vec(token_word)
        if vec is None or len(vec) == 0:
            continue
        key = "decoration_adjs_vec"
        if token_word.find("NOUN") != -1:
            is_person = person_clf.predict(vec.reshape((1, -1)))
            if is_person:
                key = "persons_vec"
            else:
                key = "decoration_vec"
        elif token_word.find("VERB") != -1:
            is_do = do_clf.predict(vec.reshape((1, -1)))
            if is_do:
                key = "do_vec"
            else:
                key = "state_vec"
        if not parsed_req.get(key, None):
            parsed_req[key] = [vec]
        else:
            parsed_req[key].append(vec)
    return get_recommendation(parsed_req)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print(message)
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Для поиска книги напиши её описание \r\n"
                                               "Чтобы написать письмо разработчику жми на /support")
        return
    if message.text == "/support":
        user_statements[message.from_user.id] = "support"
        bot.send_message(message.from_user.id, "Введите сообщение для разработчика, он обязательно его получит!")
        return

    if message.text == "/filter":
        user_statements[message.from_user.id] = "filter"
        bot.send_message(message.from_user.id, "Выберите и отрегулируйте фильтр, который для вас важен :)")
        return

    if message.text:
        print(user_statements)

        if user_statements.get(message.from_user.id, "") == "support":
            print(message.text)
            bot.send_message(message.from_user.id, "Спасибо! Думаю, Женя очень порадуется, когда прочитает это!")
            user_statements[message.from_user.id] = "book"
            return
        if user_statements.get(message.from_user.id, None) in ["book", None]:
            bot.send_message(message.from_user.id, find_book(message.text))
            return
        if user_statements.get(message.from_user.id, "") in ["filter"]:
            add_filter_for_user(message.text)


bot.polling()
