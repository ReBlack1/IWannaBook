#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import etree
import re


def get_book_metainfo(book_xml):
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

