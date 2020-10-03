import re
import time
from collections import Counter
import math
import requests
from lxml import html


class BookNotFound(Exception):
    pass


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


class LitresParser:
    def __init__(self):
        pass

    def get_html(self, author, book_name):
        book_new_name = book_name.replace(' ', '+')  # название книги привели к нужному для поискового запроса формату
        url = f'https://www.litres.ru/pages/rmd_search_arts/?q={book_new_name}'  # сформировали url
        r = requests.get(url)  # получили html поисковой страницы
        r = html.fromstring(r.content)
        names_list = r.xpath('//div[@class="art-item__name"]/a')  # вытащили все названия книг
        authors_list = r.xpath('//div[@class="art-item__author"]/a')  # вытащили всех авторов
        for i in range(0, len(names_list)):  # циклом прошли и сравнили название и автора с заддным
            if (names_list[i].text == book_name) & (authors_list[i].text == author):
                href = names_list[i].attrib['href']  # у нужной книги получили ссылочку на нее
                return requests.get(f'https://www.litres.ru{href}')  # вернули нужный html
        raise BookNotFound('BookNotFound')  # если не найдено совпадений(книга не найдена по точному совпадению автора и названия), ошибка

    def get_rating(self, author, book_name):
        ht = self.get_html(author, book_name)
        ht = html.fromstring(ht.content)
        rating = ht.xpath('//div[@class="rating-number bottomline-rating"]/text()')  # все оценки сразу
        count = ht.xpath('//div[@class="votes-count bottomline-rating-count"]/text()')
        if rating[0] != '0':  # оценки читателей есть
            rating_reader = rating[0]
            count_reader = count[0]
        else:  # оценок читателей нет
            rating_reader = count_reader = None
        try:  # если тут ничего нет, то оценки профи нет
            rating_lib = rating[1]
            count_lib = count[1]
        except IndexError:
            rating_lib = count_lib = None
        slovar = {'rating_reader': rating_reader, 'count_reader': count_reader, 'rating_lib': rating_lib,
                  'count_lib': count_lib}
        return slovar


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
    return count
