#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_manager as bm
from lxml import etree
import re


def preprocess_text(text):
    """
    Предпроцессинг текста:
    Замена url, замена ё на е, приведение в нижний регистр,
    Удаление знаков препинания,
    :param text:
    :return:
    """
    if text is None:
        return ""
    text = text.lower().replace("ё", "е")
    text = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+))', 'URL', text)
    text = re.sub(r'[^a-zA-Zа-яА-Я1-9]+', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


def add_to_graph(sintax, graph):
    sintax_dict = dict()
    sintax = sintax.split("\n")
    for word in sintax:
        if len(word) == 0 or word[0] == "#":
            continue
        word = word.replace("	", " ").split()
        if word[5] == "Foreign=Yes":  # текст не на русском
            return
        graph.add_node(word[2])
        sintax_dict[word[0]] = word[2]

    for word in sintax:
        if len(word) > 0 and word[0] != "#":
            word = word.replace("	", " ").split()
            if word[6] == "0":
                continue
            graph.add_edge(sintax_dict[word[6]], word[2], context=word[6])



from language_tools.UDPipe_api import *
import networkx as nx

G = nx.MultiGraph()

path = r"test_books\slugi.zip"
xml = bm.open_book(path)
_xpath = etree.XPath(r'//*')
dom = etree.XML(xml)
ans = _xpath(dom)
for i in ans[200:300]:
    """Обработка заголовков, автора и т.д. через i.text """
    if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
        """ Построчная обработка книги перед предпроцессингом (Только текста) """
        sintax = get_sintax(i.text)
        add_to_graph(sintax, G)

# for i in range(10):
#     print(combined_model.make_sentence(tries=30))

node_color = [G.degree(v) for v in G]
# node_size = [0.0005 * nx.get_node_attributes(G, 'population')[v] for v in G]
nx.draw(G, nlist=[G.nodes], with_labels=True, font_weight='bold', node_color = node_color)
plt.show()
