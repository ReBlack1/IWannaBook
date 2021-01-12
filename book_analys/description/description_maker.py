#!/usr/bin/env python
# -*- coding: utf-8 -*-
from text_analys.classifiers.person_classifier import PersonClassifier
import book_manager
from book_analys.mining.parser import get_book_metainfo

import networkx as nx
import time
import pickle
import config

class DescriptionMaker:
    def __init__(self):
        pass

    def add_book(self, G):
        pass


def get_short_desc(G):
    pc = PersonClassifier()
    persons = []
    things = []
    acts = []
    states = []
    for word in G:
        if "NOUN" in word:
            is_person = pc.get_classifier_by_token(word)
            if is_person is None:
                continue
            if is_person:
                persons.append((word, G.nodes[word]["size"]))
            else:
                things.append((word, G.nodes[word]["size"]))

    def sort_by_second(item):
        return item[1]

    persons.sort(key=sort_by_second, reverse=True)
    things.sort(key=sort_by_second, reverse=True)
    print(persons)
    print(things)
    # TODO материальные существительные от нематериальных
    # TODO убрать местосимения
    # TODO некоторые действия нелогичны для объектов - как отследить?
    # TODO проверки логики можно избежать если брать взаимодействия из ближашего времени
    paths = dict(nx.all_pairs_dijkstra_path(G, cutoff=2))
    print(paths[persons[6][0]][things[4][0]])


if __name__ == '__main__':
    desc_maker = DescriptionMaker()

    for book_num in range(70000, 70001):
        raw_graph_save_path = config.optimized_graph_path + r"\opt_graph_" + str(book_num) + '.plc'
        book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'

        try:
            with open(raw_graph_save_path, 'rb') as f:
                graph_dict = pickle.load(f)

            G = graph_dict["graph"]
            get_short_desc(G)
            st = time.time()
            # .add_graph(G)
            print(time.time() - st)

            print("Поведенческий граф номер {} создан :)".format(str(book_num)))
        except FileNotFoundError:
            print("Граф номер {} не найден".format(str(book_num)))