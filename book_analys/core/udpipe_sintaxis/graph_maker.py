#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base_analys.graph_manager as graph_manager
import config
import networkx as nx
import pickle

if __name__ == '__main__':

    for book_num in range(0, 50):
        G = nx.MultiGraph()
        sintax_save_path = config.sintax_path + r"\sintax_flibusta_" + str(book_num) + '.plc'
        raw_graph_save_path = config.raw_graph_path + r"\graph_flibusta_" + str(book_num) + '.plc'
        try:
            with open(sintax_save_path, 'rb') as f:
                sintax_list = pickle.load(f)
            for sentence in sintax_list:
                graph_manager.add_to_graph(sentence, G)
            with open(raw_graph_save_path, 'wb') as f:
                pickle.dump(G, f)
            print("Граф номер {} сохранен :)".format(str(book_num)))
        except FileNotFoundError:
            print("Синтаксис номер {} не найден".format(str(book_num)))