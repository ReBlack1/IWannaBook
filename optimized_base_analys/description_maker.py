#!/usr/bin/env python
# -*- coding: utf-8 -*-
import book_manager
from base_analys.base_helper import get_base_info_from_book_xml

import config
import pickle
import numpy as np
import time


class DescriptionMaker:
    def __init__(self):
        self.description_books_path = config.descriprion_book_path
        self.catalog = None

    def add_new_description(self, G, vectors, index, book_id, info):
        weights = np.ndarray(shape=(len(index)), dtype=int)
        for i in range(len(index)):
            word = index[i]
            size = G.nodes[word]["size"]
            weights[i] = size

        last_book = len(self.catalog['info'])
        average_vector = np.average(vectors[:len(index)], axis=0, weights=weights)
        self.catalog['vectors'][last_book] = average_vector
        self.catalog["info"].append({"book_id": book_id, "book_info": book_info})

        if len(self.catalog["info"]) != last_book + 1:
            raise Exception("Нарушение целостности данных между инфой и векторами")

        # if len(self.catalog["info"]) % 100 == 0:  # На каждую сотку книг - сохрание
        #     self.save_dict()

    def save_dict(self):
        with open(self.description_books_path, 'wb') as f:
            pickle.dump({"vectors": self.catalog["vectors"][:len(self.catalog["info"])], "info": self.catalog["info"]}, f)

    def make_new_desc(self):
        self.catalog = {"vectors": np.ndarray(shape=(300000, 300), dtype=float), "info": []}

    def upload_desc(self, path=config.descriprion_book_path):
        with open(path, 'rb') as f:
            self.catalog = pickle.load(f)


if __name__ == '__main__':
    desc_maker = DescriptionMaker()
    desc_maker.make_new_desc()

    for book_num in range(70000, 70429):
        raw_graph_save_path = config.optimized_graph_path + r"\opt_graph_" + str(book_num) + '.plc'
        book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'

        try:

            with open(raw_graph_save_path, 'rb') as f:
                graph_dict = pickle.load(f)
            st = time.time()

            book_xml = book_manager.open_book(book_path)
            book_info = get_base_info_from_book_xml(book_xml)

            desc_maker.add_new_description(graph_dict["graph"],
                                           graph_dict["vectors"],
                                           graph_dict["book_word_list"],
                                           book_num,
                                           book_info)
            print(time.time() - st)

            print("Описание номер {} обработано :)".format(str(book_num)))
        except FileNotFoundError:
            print("Граф номер {} не найден".format(str(book_num)))

    desc_maker.save_dict()
