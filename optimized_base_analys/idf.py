#!/usr/bin/env python
# -*- coding: utf-8 -*-
import book_manager
from base_analys.base_helper import get_base_info_from_book_xml

import math
import config
import pickle
import time

class Idf:
    def __init__(self):
        self.df_dict = dict()  # слово: встречаемость
        self.q_doc = 0

    def add_doc(self, word_set):
        for word in word_set:
            if self.df_dict.get(word, None):  # Уже есть в словаре
                self.df_dict[word] += 1
            else:
                self.df_dict[word] = 1

        self.q_doc += 1
        return self.q_doc

    def get_idf(self, word):
        if not self.df_dict.get(word, None):
            raise Exception("Требуется сначала добавить документ в список idf, с помощью Idf.add_doc")
        return math.log10(self.q_doc / self.df_dict[word])

    def save(self, path=config.idf_path):
        with open(path, 'wb') as f:
            pickle.dump({"df_dict": self.df_dict, "q_doc": self.q_doc}, f)

    def load(self, path=config.idf_path):
        with open(path, 'rb') as f:
            idf_dict = pickle.load(f)
            self.df_dict = idf_dict["df_dict"]
            self.q_doc = idf_dict["q_doc"]


if __name__ == '__main__':
    idf_maker = Idf()

    for book_num in range(70000, 70429):
        raw_graph_save_path = config.optimized_graph_path + r"\opt_graph_" + str(book_num) + '.plc'
        book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'

        try:

            with open(raw_graph_save_path, 'rb') as f:
                graph_dict = pickle.load(f)
            G = graph_dict["graph"]
            st = time.time()

            book_xml = book_manager.open_book(book_path)
            book_info = get_base_info_from_book_xml(book_xml)

            idf_maker.add_doc(G.nodes.keys())
            print(time.time() - st)

            print("Описание номер {} обработано :)".format(str(book_num)))
        except FileNotFoundError:
            print("Граф номер {} не найден".format(str(book_num)))

    print(idf_maker.get_idf("идти_VERB"))