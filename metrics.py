import re
import time
from collections import Counter
import math
import requests
from bs4 import BeautifulSoup


class BookNotFound(Exception):
    pass

class LitresParser:
    def __init__(self):
        pass

    def get_all_books(book_name):
        book_new_name = book_name.replace(' ', '+')  # название книги привели к нужному для поискового запроса формату
        url = f'https://www.litres.ru/pages/rmd_search_arts/?q={book_new_name}'  # сформировали url
        r = requests.get(url).text  # получили html поисковой страницы
        soup = BeautifulSoup(r, 'lxml')
        books = soup.find_all("div", {"class": "art-item search__item item__type_art"}) # получили информацию о всех книгах из поиска
        return books

    def get_book(books, author, book_name):
        authors_list = [] # список авторов всех произведений. Если автор не указан, то значение ''
        names_list = [] # список названий всех произведений
        for book in books:  # в цикле проходим по всем книгам и заполняем список авторов и названий
            authors_list.append(book.find_all('a')[-1])
            names_list.append(book.find_all('a')[1])
        for i in range(0, len(names_list)): # в цикле идем по всем авторам и названиям, ищем точное совпадение названия и автора
            if (names_list[i].text == book_name) & (authors_list[i].text == author):
                href = names_list[i].get('href')  # у нужной книги получили ссылочку на нее
                return requests.get(f'https://www.litres.ru{href}').text  # вернули нужный html
        raise BookNotFound('BookNotFound')  # если не найдено совпадений(книга не найдена по точному совпадению автора и названия), ошибка

    def get_rating(author, book_name):
        html_all_books = LitresParser.get_all_books(book_name)  # получили информацию о всех книгах из поиска
        html_book = LitresParser.get_book(html_all_books, author, book_name)    # получили информацию о конкретной книге
        soup = BeautifulSoup(html_book, 'lxml')
        rating = soup.find_all("div", {"class": "rating-number bottomline-rating"})  # все оценки сразу(в форме веб элемента)
        count = soup.find_all("div", {"class": "votes-count bottomline-rating-count"})
        if rating and rating[0].text != '0':  # оценки читателей есть
            rating_reader = rating[0].text
            count_reader = count[0].text
        else:  # оценок читателей нет
            rating_reader = count_reader = None
        try:  # если тут ничего нет, то оценки профи нет
            rating_lib = rating[1].text
            count_lib = count[1].text
        except IndexError:
            rating_lib = count_lib = None
        slovar = {'rating_reader': rating_reader, 'count_reader': count_reader, 'rating_lib': rating_lib,
                  'count_lib': count_lib}
        return slovar


def transliterate(name):
    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '-', '~': '', '.': '', '!': '', '@': '', '#': '',
              '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '-', '=': '', '+': '',
              ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
              '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
              'Є': 'e', '—': ''}
    for key in slovar:
        name = name.replace(key, slovar[key])
    return name


def compute_tf(text):
    tf_text = Counter(text)
    for i in tf_text:
        tf_text[i] = tf_text[i] / float(len(text))
    return tf_text


def compute_idf(word, corpus):
    return math.log10(len(corpus) / sum([1.0 for i in corpus if word in i]))


def compute_tfidf(count_books):
    """
    Определяет TF-IDF
    """
    for i in range(0, count_books):
        # открыть файл с текстом.
        tf_dict = compute_tf('')  # пихнуть сюда
        # если tf содержался, то увеличить на 1 счетчик(словарь знаменателя). если не содержался, то добавить новую пару
        # сохранить результаты в другой папке через pickle

    # создать словарь с посчитанными idf. сохранить его
    documents_list = []
    for text in corpus:
        tf_idf_dictionary = {}
        computed_tf = compute_tf(text)
        for word in computed_tf:
            tf_idf_dictionary[word] = computed_tf[word] * compute_idf(word, corpus)
        documents_list.append(tf_idf_dictionary)
    return documents_list


def is_mat(word):
    """
    Определяет является слово бранным или нет
    """
    _mats = {r'(ху(й|е|ё|и|я|ли[^а-я])\w*)',
             r'(п(и|е|ё)(з|с)д)\w*',
             r'([^а-я])(би?ля(д|т|[^а-я]))\w*',
             r'(пид(о|а)р|п(е|и)дри)\w*',
             r'(муд(ак|ач|о|и))\w*',
             r'(([^а-я]|по|на|от|не|ни)(х|x)(е|e)(р|p))\w*',
             r'(з(а|о)луп(а|и))\w*',
             r'(([^а-я]у?|под?|на|за|от|вы|ь|ъ)(е|ё|и)б(а|ыр|у|нут|ись|ище))\w*',
             r'([^а-я])((на|по)х)([^а-я])\w*',
             r'(су(ка|чк|ки|чь))\w*',
             r'(др(оч|ачи))\w*',
             r'((\W|о|за)трах)\w*'}
    for reg in _mats:
        if re.search(reg, word) is not None:
            return True
    return False


def count_mats(text):
    """
    Считает количество бранных слов в тексте
    """
    text = text.lower()
    word = re.split('!?;-| |, |\n', text)
    count = 0
    for slovo in word:
        if is_mat(slovo):
            count += 1
            # print(slovo)
    return count


# text = 'превысокомногорассмотрительствующий ' * 30000
# while True:
#    x = input()
#    if x:
#        text += x + '\n'
#    else:
#        break
# start = time.time()
# print(count_mats(text))
# end = time.time()
# print(f'{end-start} секунд')
try:
    print(LitresParser.get_rating('Гусейн Аббасзаде', 'Просьба'))
except BookNotFound as e:
    print(e)
try:
    print(LitresParser.get_rating('Рик Янси', '5-я волна'))
except BookNotFound as e:
    print(e)
try:
    print(LitresParser.get_rating('Рик Янси', '5я волна'))
except BookNotFound as e:
    print(e)
try:
    print(LitresParser.get_rating('Рик нси', '5-я волна'))
except BookNotFound as e:
    print(e)
try:
    print(LitresParser.get_rating('Александр Пушкин', 'Капитанская дочка'))
except BookNotFound as e:
    print(e)
try:
    print(LitresParser.get_rating('Лора Вандеркам', 'Школа Джульетты. История о победе над цейтнотом и выгоранием'))
except BookNotFound as e:
    print(e)
try:
    print(LitresParser.get_rating('Марина Тёмкина', 'Ненаглядные пособия (сборник)'))
except BookNotFound as e:
    print(e)
try:
    print(LitresParser.get_rating('Кеннет Райт','Великолепная Лола'))
except BookNotFound as e:
    print(e)

# print(get_rating('Рик Янси', '5-я волна'))

# corpus = [['pasta', 'la', 'vista', 'baby', 'la', 'vista'],
# ['hasta', 'siempre', 'comandante', 'baby', 'la', 'siempre'],
# ['siempre', 'comandante', 'baby', 'la', 'siempre']]
# print(compute_tfidf(corpus))
