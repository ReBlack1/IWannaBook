#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import networkx as nx
import pickle
import tokenizer
import pymorphy2
import numpy as np
import optimized_base_analys.analys_const as const
import client
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

class GraphMaker:
    def __init__(self, book_num):
        self.morph = pymorphy2.MorphAnalyzer()

        self.G = nx.MultiDiGraph()
        self.sentence_num = 0

        self.vectors = np.ndarray(shape=(10000, 300), dtype=float)  # 0 строк, 300 столбцов
        self.book_word_list = []  # index: token_word - для перехода к графу - last_word_num = len(book_word_list)
        self.synonim_dict = dict()

        self.sintax_save_path = config.optimized_sintax_path + r"\opt_sinx_" + str(book_num) + '.zip'
        self.raw_graph_save_path = config.optimized_graph_path + r"\opt_graph_" + str(book_num) + '.plc'

    def make_graph(self, sintax_list):
        for sentence in sintax_list:
            replace_token = dict()
            for word in sentence[0]:  # Перебор слов
                node_name = self.add_node_to_graph(word)
                replace_token[word] = node_name
            for edge in sentence[1]:  # Перебор связей
                from_node = sentence[0][edge[1]]
                to_node = sentence[0][edge[0]]
                self.add_edge_to_graph(from_node, to_node, edge[2])

            self.sentence_num += 1
        return self.G

    def get_similar_vec(self, target):
        most_similar_sklearn = cosine_similarity(target, self.vectors[:len(self.book_word_list) + 1])
        return np.argmax(most_similar_sklearn), np.max(most_similar_sklearn)

    def add_node_to_graph(self, node):
        token_node = tokenizer.get_stat_token_word(self.morph, node)

        if not token_node:  # Слово не токенизируется - скорее всего мусор. TODO собрать массив нетокенизируемых слов
            return None

        if self.G.nodes.get(token_node, None):  # Слово уже есть в графе
            self.G.nodes[token_node].update(size=self.G.nodes[token_node]["size"] + 1)
            return token_node

        if self.synonim_dict.get(token_node, None):
            synonim_word = self.synonim_dict.get(token_node, None)
            self.G.nodes[synonim_word].update(size=self.G.nodes[synonim_word]["size"] + 1)
            return synonim_word

        node_vec = client.get_vec(token_node)
        if node_vec.size == 0:
            return None
        node_vec = np.reshape(node_vec, (1, 300))

        max_index, max_similarity = self.get_similar_vec(node_vec)

        if max_similarity > const.synonim_dist:  # Новое слово - синоним существующего
            synonim_word = self.book_word_list[max_index]
            # print("Синонимы: ", synonim_word, token_node, max_similarity)
            self.G.nodes[synonim_word].update(size=self.G.nodes[synonim_word]["size"] + 1)
            self.synonim_dict[token_node] = synonim_word
            return synonim_word

        self.G.add_node(token_node, size=1)
        self.vectors[len(self.book_word_list)] = node_vec
        self.book_word_list.append(token_node)

        return token_node  # по этому ключу буду искать потом

    def add_edge_to_graph(self, from_node, to_node, edge_type):
        from_node = tokenizer.get_stat_token_word(self.morph, from_node)
        to_node = tokenizer.get_stat_token_word(self.morph, to_node)
        if not from_node or not to_node:
            return

        from_node = self.synonim_dict.get(from_node, from_node)
        to_node = self.synonim_dict.get(to_node, to_node)

        self.G.add_edge(from_node, to_node, time=self.sentence_num, type=edge_type)

if __name__ == '__main__':
    for book_num in range(70000, 70050):
        sintax_save_path = config.optimized_sintax_path + r"\opt_sinx_" + str(book_num) + '.zip'
        raw_graph_save_path = config.optimized_graph_path + r"\opt_graph_" + str(book_num) + '.plc'
        try:
            import time
            with open(sintax_save_path, 'rb') as f:
                sintax_list = pickle.load(f)
            st = time.time()

            GM = GraphMaker(book_num)
            G = GM.make_graph(sintax_list)
            print(time.time() - st)

            node_color = [(G.degree(v)) * 3 for v in G.nodes]
            # sizes = nx.get_node_attributes(G, 'size')
            # node_size = [400 * sizes[v] for v in G.nodes]
            nx.draw(G, nlist=[G.nodes], with_labels=True, node_color=node_color, font_color="k")
            plt.show()
            exit()
            with open(raw_graph_save_path, 'wb') as f:
                pickle.dump(G, f)
            print("Граф номер {} сохранен :)".format(str(book_num)))
        except FileNotFoundError:
            print("Синтаксис номер {} не найден".format(str(book_num)))