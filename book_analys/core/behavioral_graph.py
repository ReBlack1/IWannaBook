#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config
import networkx as nx
import pickle
import time


class BehavioralGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.temp_dict = {"VERB": [], "ADJ": [], "ADV": []}

    def add_graph(self, G):
        for word in G.nodes:
            voice_part = word.split("_")[1]
            if voice_part == "NOUN":
                self.graph.add_node(word, adjs=[])
            elif voice_part in ["VERB", "GRND", 'PRTS', 'PRTF']:
                self.temp_dict["VERB"].append(word)
            elif voice_part in ["ADJ", 'NUMR']:
                self.temp_dict["ADJ"].append(word)
            elif voice_part in ['ADV']:
                self.temp_dict["ADV"].append(word)
            elif voice_part in ["ADV", 'PRED', 'PROPN', 'INTJ']:
                continue
            else:
                print(word)
                exit()

        for verb in self.temp_dict['VERB']:
            edges = G.in_edges(verb)
            print(edges)

            edges = G.out_edges(verb)
            edges = G.edges(verb)
            print(dir(edges))
            print([G.get_edge_data(verb, neigh) for neigh in G.successors(verb)])
            exit()


if __name__ == '__main__':
    b_graph = BehavioralGraph()

    for book_num in range(70000, 70001):
        raw_graph_save_path = config.optimized_graph_path + r"\opt_graph_" + str(book_num) + '.plc'
        book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'

        try:
            with open(raw_graph_save_path, 'rb') as f:
                graph_dict = pickle.load(f)

            G = graph_dict["graph"]

            st = time.time()
            b_graph.add_graph(G)
            print(time.time() - st)

            print("Поведенческий граф номер {} создан :)".format(str(book_num)))
        except FileNotFoundError:
            print("Граф номер {} не найден".format(str(book_num)))
