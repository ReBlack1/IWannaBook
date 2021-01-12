#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cProfile

import config
import networkx as nx
import pickle
from text_analys.mining import tokenizer
import numpy as np
import book_analys.core.analys_const as const
from sklearn.utils.extmath import safe_sparse_dot
import time
from sklearn.preprocessing import normalize

from gensim.models import KeyedVectors as KeyVec


class GraphMaker:
    def __init__(self, book_num, cur_model, tokenizator):
        self.tokenizator = tokenizator

        self.G = nx.MultiDiGraph()
        self.sentence_num = 0

        self.vectors = np.ndarray(shape=(10000, 300), dtype=float)
        self.normalized_vectors = np.ndarray(shape=(10000, 300), dtype=float)  # Оптимизация для косинусной близости

        self.book_word_list = []  # index: token_word - для перехода к графу - last_word_num = len(book_word_list)
        self.synonim_dict = dict()
        self.q_word = 0

        self.sintax_save_path = config.optimized_sintax_path + r"\opt_sinx_" + str(book_num) + '.zip'
        self.raw_graph_save_path = config.optimized_graph_path + r"\opt_graph_" + str(book_num) + '.plc'
        self.cur_model = cur_model

    def make_graph(self, sintax_list):
        for sentence in sintax_list:
            for word in sentence[0]:  # Перебор слов
                self.add_node_to_graph(word)

            for edge in sentence[1]:  # Перебор связей
                from_node = sentence[0][edge[1]]
                to_node = sentence[0][edge[0]]
                self.add_edge_to_graph(from_node, to_node, edge[2])

            self.sentence_num += 1

        return {"graph": self.G, "vectors": self.vectors[:len(self.book_word_list)], "book_word_list": self.book_word_list}

    def get_similar_vec(self, target):
        norm_target = normalize(target, copy=True)
        if len(self.book_word_list) == 0:
            return None, None, norm_target
        most_similar_sklearn = safe_sparse_dot(norm_target, self.normalized_vectors[:len(self.book_word_list)].T, dense_output=True)
        return np.argmax(most_similar_sklearn), np.max(most_similar_sklearn), norm_target

    def add_node_to_graph(self, node):
        token_node = self.tokenizator.get_stat_token_word(node)

        if not token_node:  # Слово не токенизируется - скорее всего мусор. TODO собрать массив нетокенизируемых слов
            return None

        self.q_word += 1

        if self.G.nodes.get(token_node, None):  # Слово уже есть в графе
            self.G.nodes[token_node].update(size=self.G.nodes[token_node]["size"] + 1)
            return token_node

        if self.synonim_dict.get(token_node, None):  # Синоним слова уже есть в графе и слово повторяется
            synonim_word = self.synonim_dict.get(token_node, None)
            self.G.nodes[synonim_word].update(size=self.G.nodes[synonim_word]["size"] + 1)
            return synonim_word

        node_vec = self.get_vector_from_model(token_node)
        if node_vec is None or node_vec.size == 0:
            return None
        node_vec = np.reshape(node_vec, (1, 300))

        max_index, max_similarity, norm_vector = self.get_similar_vec(node_vec)

        if max_similarity and max_similarity > const.synonim_dist:  # Новое слово - синоним существующего
            synonim_word = self.book_word_list[max_index]
            # print("Синонимы: ", synonim_word, token_node, max_similarity)
            self.G.nodes[synonim_word].update(size=self.G.nodes[synonim_word]["size"] + 1)
            self.synonim_dict[token_node] = synonim_word
            return synonim_word

        self.G.add_node(token_node, size=1)
        self.vectors[len(self.book_word_list)] = node_vec
        self.normalized_vectors[len(self.book_word_list)] = norm_vector
        self.book_word_list.append(token_node)

        return token_node  # по этому ключу буду искать потом

    def add_edge_to_graph(self, from_node, to_node, edge_type):
        from_node = self.tokenizator.get_stat_token_word(from_node)
        to_node = self.tokenizator.get_stat_token_word(to_node)
        if not from_node or not to_node:
            return

        from_node = self.synonim_dict.get(from_node, from_node)
        to_node = self.synonim_dict.get(to_node, to_node)

        self.G.add_edge(from_node, to_node, time=self.sentence_num, type=edge_type)

    def get_vector_from_model(self, word):
        try:
            return self.cur_model.get_vector(word)
        except KeyError:
            return None


if __name__ == '__main__':
    print("Загрузка модели: ", end="")
    tayga_model = r"D:\py_projects\IWonnaBook\models\tayga_2019\model.txt"
    cur_model = KeyVec.load_word2vec_format(tayga_model)
    print("Завершена.")

    tokenizator = tokenizer.Tokenizator()

    for book_num in range(70000, 70001):
        sintax_save_path = config.optimized_sintax_path + r"\opt_sinx_" + str(book_num) + '.zip'
        graph_save_path = config.optimized_graph_path + r"\opt_graph_" + str(book_num) + '.plc'
        try:
            with open(sintax_save_path, 'rb') as f:
                sintax_list = pickle.load(f)

            st = time.time()
            GM = GraphMaker(book_num, cur_model, tokenizator)
            # cProfile.run("GM.make_graph(sintax_list)")
            G = GM.make_graph(sintax_list)
            with open(graph_save_path, 'wb') as f:
                pickle.dump(G, f)
            print("Граф номер {} сохранен :)".format(str(book_num)))
        except FileNotFoundError:
            print("Синтаксис номер {} не найден".format(str(book_num)))