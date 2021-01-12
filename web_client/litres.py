#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


class BookNotFound(Exception):
    pass


class CaptchaException(Exception):
    pass


class LitresParser:
    def __init__(self, proxy=None):
        self.proxies = proxy

    def set_proxy(self, proxy):
        self.proxies = proxy

    def get_all_books(self, book_name):
        book_new_name = book_name.replace(' ', '+')  # название книги привели к нужному для поискового запроса формату
        url = f'https://www.litres.ru/pages/rmd_search_arts/?q={book_new_name}'  # сформировали url
        r = requests.get(url, proxies=self.proxies, timeout=8).text  # получили html поисковой страницы
        pos = r.find("Подтвердите, что вы не робот")
        if pos != -1:
            raise CaptchaException
        soup = BeautifulSoup(r, 'lxml')
        books = soup.find_all("div", {"class": "art-item search__item item__type_art"})  # получили информацию о всех книгах из поиска
        return books

    def get_book(self, books, author, book_name):
        authors_list = []  # список авторов всех произведений. Если автор не указан, то значение ''
        names_list = []  # список названий всех произведений
        for book in books:  # в цикле проходим по всем книгам и заполняем список авторов и названий
            authors_list.append(book.find_all('a')[-1])
            names_list.append(book.find_all('a')[1])
        for i in range(0, len(names_list)):  # в цикле идем по всем авторам и названиям, ищем точное совпадение названия и автора
            if (names_list[i].text == book_name) & (authors_list[i].text == author):
                href = names_list[i].get('href')  # у нужной книги получили ссылочку на нее
                return requests.get(f'https://www.litres.ru{href}', proxies=self.proxies, timeout=8).text  # вернули нужный html
        raise BookNotFound('BookNotFound')  # если не найдено совпадений(книга не найдена по точному совпадению автора и названия), ошибка

    def get_rating(self, author, book_name):
        try:
            html_all_books = self.get_all_books(book_name)  # получили информацию о всех книгах из поиска
        except CaptchaException:
            raise CaptchaException
        html_book = self.get_book(html_all_books, author, book_name)    # получили информацию о конкретной книге
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


import web_client.proxy as prx

proxies = {**prx.get_proxy(['https']), **prx.get_proxy(['http'])}
print(proxies)
litres = LitresParser(proxies)
print(litres.get_rating('Фридрих Шиллер', 'Разбойники'))

