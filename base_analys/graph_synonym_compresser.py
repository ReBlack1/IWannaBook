#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import networkx as nx  # Возможно требуется для pickle.load(f)
import pickle
from scipy.spatial.distance import cosine
from base_analys.word_manager import is_pronoun
import pymorphy2
import tokenizer
import json
import client
from base_analys.graph_manager import combine_nodes
import requests
import numpy as np


def get_vec(token_word):
    data = json.dumps({"method": "get_vec", "params": [token_word]})
    res = requests.post("http://127.0.0.1:9095/", data)
    vec = np.frombuffer(res.content, dtype="float32")
    return vec


def get_word(vec):
    vec_list = vec.tolist()
    data = json.dumps({"method": "get_similar_word", "params": [vec_list]})
    res = requests.post("http://127.0.0.1:9095/", data)
    return json.loads(res.content)["res"]


def merge_synonims(G, vec_list, word_list, threshold=0.5):
    size = len(vec_list)
    for base in range(size):  # Объединяем синонимы существительныз
        for comp in range(base + 1, size):
            if cosine(vec_list[base], vec_list[comp]) < threshold:  # Если слова - синонимы
                old_name1 = noun_word_list[base]
                old_name2 = noun_word_list[comp]
                new_vec = (vec_list[base] + vec_list[comp]) / 2

                new_name = get_word(new_vec)[0][0].split("_")[0]  # Первое слово, слово (Второе - близость), отрезаем токен
                try:
                    combine_nodes(old_name1, old_name2, new_name, G)
                except KeyError:  # Слово уже было и его удалили
                    continue
                for word in range(len(word_list)):
                    if word_list[word] in [old_name1, old_name2]:
                        word_list[word] = new_name


if __name__ == '__main__':
    morph = pymorphy2.MorphAnalyzer()

    for book_num in range(0, 50):
        raw_graph_save_path = config.raw_graph_path + r"\graph_flibusta_" + str(book_num) + '.plc'
        compressed_graph_save_path = config.raw_graph_path + r"\tayga_commpressed_graph_flibusta_" + str(book_num) + '.plc'

        try:
            with open(raw_graph_save_path, 'rb') as f:
                G = pickle.load(f)

            alone_node_list = []  # Удалим вершины без ребер
            for node in G:
                if not G[node]:  # Если множество ребер для вершины пусто
                    alone_node_list.append(node)
            for node in alone_node_list:
                G.remove_node(node)

            # Обединим синонимы
            noun_word_list = []
            noun_vec_list = []
            verb_word_list = []
            verb_vec_list = []

            for word in G:  # Соберем вектора для объединения синонимов
                if is_pronoun(word):  # Метоимения не объединяем
                    continue
                token_word = tokenizer.get_stat_token_word(morph, word)
                if token_word is None:
                    continue
                vec = get_vec(token_word)
                if len(vec) == 0:
                    continue

                if token_word.find("NOUN") != -1:  # Пока объединим только существительные
                    noun_word_list.append(word)
                    noun_vec_list.append(vec)
                if token_word.find("VERB") != -1:  # объединяем глаголы
                    verb_word_list.append(word)
                    verb_vec_list.append(vec)

            merge_synonims(G, noun_vec_list, noun_word_list)
            merge_synonims(G, verb_vec_list, verb_word_list)

            with open(raw_graph_save_path, 'wb') as f:
                pickle.dump(G, f)
            print("Граф номер {} сохранен :)".format(str(book_num)))
        except FileNotFoundError:
            print("Граф номер {} не найден".format(str(book_num)))