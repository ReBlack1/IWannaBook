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
                vec = client.get_vec(token_word)
                if len(vec) == 0:
                    continue

                if token_word.find("NOUN") != -1:  # Пока объединим только существительные
                    noun_word_list.append(word)
                    noun_vec_list.append(vec)
                if token_word.find("VERB") != -1:  # объединяем глаголы
                    verb_word_list.append(word)
                    verb_vec_list.append(vec)

            size = len(noun_vec_list)
            for base in range(size):  # Объединяем синонимы существительныз
                for comp in range(base + 1, size):
                    if cosine(noun_vec_list[base], noun_vec_list[comp]) < 0.5:
                        old_name1 = noun_word_list[base]
                        old_name2 = noun_word_list[comp]
                        if old_name1 == old_name2:
                            continue
                        new_vec = (noun_vec_list[base] + noun_vec_list[comp]) / 2
                        res = json.loads(client.get_word_by_vec(new_vec.tostring()).decode())["res"][0]
                        new_name = res[0].split("_")[0]
                        combine_nodes(old_name1, old_name2, new_name, G)
                        for word in range(len(noun_word_list)):
                            if noun_word_list[word] in [old_name1, old_name2]:
                                noun_word_list[word] = new_name

            size = len(verb_vec_list)
            for base in range(size):  # Объединяем синонимы глаголов
                for comp in range(base + 1, size):
                    if cosine(verb_vec_list[base], verb_vec_list[comp]) < 0.5:
                        old_name1 = verb_word_list[base]
                        old_name2 = verb_word_list[comp]
                        if old_name1 == old_name2:
                            continue
                        new_vec = (verb_vec_list[base] + verb_vec_list[comp]) / 2
                        res = json.loads(client.get_word_by_vec(new_vec.tostring()).decode())["res"][0]
                        new_name = res[0].split("_")[0]
                        combine_nodes(old_name1, old_name2, new_name, G)
                        for word in range(len(verb_word_list)):
                            if verb_word_list[word] in [old_name1, old_name2]:
                                verb_word_list[word] = new_name

            with open(raw_graph_save_path, 'wb') as f:
                pickle.dump(G, f)
            print("Граф номер {} сохранен :)".format(str(book_num)))
        except FileNotFoundError:
            print("Синтаксис номер {} не найден".format(str(book_num)))