#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_manager
from metrics import LitresParser, BookNotFound
import zipfile
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


if __name__ == '__main__':
    for book_num in range(50497, 60000):
        book_path = r'E:\books\flibusta_' + str(book_num) + '.zip'
        try:
            book_xml = book_manager.open_book(book_path)
            book_info = get_base_info_from_book_xml(book_xml)
            print(book_num, book_info)
            rating = LitresParser.get_rating(book_info['author_name'] + " " + book_info['author_second_name'],
                                       book_info['title'])
            print(rating)
            break
        except zipfile.BadZipFile:
            # book = open(book_path, 'r', encoding='utf8')
            continue  # Там есть полезная инфа, но книги нет
        except BookNotFound:
            print("книга не найдена")
        except IndexError as e:
            print("Ошибка в поиске")
            print(e.args)
            exit()

        except etree.XMLSyntaxError:
            print("Ошибка в парсинге")


