#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_manager
from base_analys.base_helper import get_base_info_from_book_xml
import config
import time
from lxml import etree
import re

from ipymarkup import show_dep_ascii_markup as show_markup  # Для красивого вывода синтаксиса
from razdel import sentenize, tokenize
from navec import Navec
from slovnet import Syntax

import pickle
import zipfile

def get_sintax_list_with_navec(syntax_parser, book_xml):
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(book_xml)
    ans = _xpath(dom)

    sintax_list = []
    chunk = []

    for i in ans:
        """Обработка заголовков, автора и т.д. через i.text """
        if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
            if not i.text:
                continue
            """ Построчная обработка книги перед предпроцессингом (Только текста) """
            tokens = [_.text for _ in tokenize(i.text)]
            if tokens:
                chunk.append(tokens)
    syntax_map = syntax_parser.map(chunk)

    for markup in syntax_map:
        # nvert CoNLL-style format to source, target indices
        words, deps = [], []
        for token in markup.tokens:
            words.append(token.text)
            source = int(token.head_id) - 1
            target = int(token.id) - 1
            if source > 0 and source != target:  # skip root, loops
                deps.append([source, target, token.rel])
        sintax_list.append((words, deps))
    return sintax_list


if __name__ == '__main__':

    navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
    syntax_parser = Syntax.load('slovnet_syntax_news_v1.tar')
    syntax_parser.navec(navec)

    for book_num in range(70162, 160000):
        book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'
        optimized_sintax_path = config.optimized_sintax_path + r'\opt_sinx_' + str(book_num) + '.zip'
        try:
            book_xml = book_manager.open_book(book_path)
            # book_info = get_base_info_from_book_xml(book_xml)
            print(book_num)

            sintax_list = get_sintax_list_with_navec(syntax_parser, book_xml)

            with open(optimized_sintax_path, 'wb') as f:
                clf = pickle.dump(sintax_list, f)
                print("Сохранено :) ")
        except zipfile.BadZipFile:
            # book = open(book_path, 'r', encoding='utf8')
            continue  # Там есть полезная инфа, но книги нет
        except IndexError as e:
            print("Ошибка в поиске")
            print(e.args)
        except etree.XMLSyntaxError:
            print("Ошибка в парсинге")