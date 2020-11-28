#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_manager
from language_tools.udpipe import UDPipe
from base_analys.base_helper import get_base_info_from_book_xml, get_sintax_list
import config
import time
from lxml import etree
import re


from ipymarkup import show_dep_ascii_markup as show_markup
from razdel import sentenize, tokenize
from navec import Navec
from slovnet import Syntax

import multiprocessing
print(multiprocessing.cpu_count())

"""
def f(x):
    while 1:
        pass  # infinite loop

import multiprocessing as mp
n_cores = mp.cpu_count()
with mp.Pool(n_cores) as p:
    p.map(f, range(n_cores))
"""

exit()

def get_sintax_list2(syntax, book_xml):
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
            chunk.append(tokens)
    syntax_map = syntax.map(chunk)

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
    # udpipe = UDPipe()
    book_num = 40000
    book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'
    book_xml = book_manager.open_book(book_path)
    book_info = get_base_info_from_book_xml(book_xml)
    print(book_num, book_info)


    # st = time.time()
    # sintax_list = get_sintax_list(udpipe, book_xml)
    # print(time.time() - st)

    navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
    syntax_parser = Syntax.load('slovnet_syntax_news_v1.tar')
    syntax_parser.navec(navec)

    st = time.time()
    for i in range(50):
        sint = get_sintax_list2(syntax_parser, book_xml)
    print(time.time() - st)
    for i in sint:
        words, deps = i
        if words and deps:
            show_markup(words, deps)
        print()
        print()
