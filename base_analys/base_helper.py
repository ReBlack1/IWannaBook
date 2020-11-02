#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import etree
import re


def get_base_info_from_book_xml(book_xml):
    # TODO Перейти на нормальный парсинг xml
    # TODO Учесть возможность нескольких авторов и т.д.
    book_info = {'author_name': "", 'author_second_name': '', 'title': '', 'genre': '', 'lang': ''}
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(book_xml)
    ans = _xpath(dom)
    for i in ans:
        if re.search(r"first-name", i.tag) is not None and i.text:
            book_info['author_name'] = i.text
        if re.search(r"last-name", i.tag) is not None and i.text:
            book_info['author_second_name'] = i.text
        if re.search(r"book-title", i.tag) is not None and i.text:
            book_info['title'] = i.text
        if re.search(r"genre", i.tag) is not None and i.text:
            book_info['genre'] = i.text
        if re.search(r"lang", i.tag) is not None and i.text:
            book_info['lang'] = i.text
        if '' not in book_info.values():  # Мы все получили
            break
    return book_info

def get_sintax_list(udpipe_obj, book_xml):
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(book_xml)
    ans = _xpath(dom)

    sintax_list = []

    for i in ans:
        """Обработка заголовков, автора и т.д. через i.text """
        if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
            if not i.text:
                continue
            """ Построчная обработка книги перед предпроцессингом (Только текста) """
            sintax = udpipe_obj.get_sintax(i.text)
            sintax_list.append(sintax)
    return sintax_list
