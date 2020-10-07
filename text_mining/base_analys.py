#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_manager
from metrics import LitresParser, BookNotFound
import zipfile
from lxml import etree
import re
from udpipe import UDPipe
import pickle

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


if __name__ == '__main__':
    udpipe = UDPipe()
    for book_num in range(0, 100000):
        book_path = r'E:\books\flibusta_' + str(book_num) + '.zip'
        try:
            book_xml = book_manager.open_book(book_path)
            book_info = get_base_info_from_book_xml(book_xml)
            print(book_num, book_info)
            # rating = LitresParser.get_rating(book_info['author_name'] + " " + book_info['author_second_name'],
            #                            book_info['title'])
            # print(rating)
            sintax_list = get_sintax_list(udpipe, book_xml)
            sintax_save_path = r"E:\sintax_lists\sintax_flibusta_" + str(book_num) + '.plc'
            with open(sintax_save_path, 'wb') as f:
                clf = pickle.dump(sintax_list, f)
                print("Сохранено :) ")
        except zipfile.BadZipFile:
            # book = open(book_path, 'r', encoding='utf8')
            continue  # Там есть полезная инфа, но книги нет
        except BookNotFound:
            print("книга не найдена")
        except IndexError as e:
            print("Ошибка в поиске")
            print(e.args)
        except etree.XMLSyntaxError:
            print("Ошибка в парсинге")


