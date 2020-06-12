#!/usr/bin/env python
# coding: utf-8
import json
import requests as req
import matplotlib.pyplot as plt
import networkx as nx

def get_sintax(text):

    url = "http://lindat.mff.cuni.cz/services/udpipe/api/process?tokenizer&tagger&parser&"
    model = "&model=russian-syntagrus-ud-2.0-170801"
    data = "data=" + text
    final_url = url + data + model

    rep = req.get(final_url)
    return json.loads(rep.content.decode())["result"]

# sintax = get_sintax("Мама мыла рамы мылом").split("\n")
# for word in sintax:
#     print(word)
#     if len(word) > 0 and word[0] != "#":
#         # print(word.split("	")[6])
#         pass


# G = nx.DiGraph()
# G.add_node("hello")
# G.add_nodes_from([2, 3])
# G.add_edge(2, "hello", weight=0.84*2)
# G.add_edge(2, 3, weight=0.84, node_color='#ff0000')
# G[2]["hello"]['weight'] *= 2
# nx.draw(G, nlist=[G.nodes], with_labels=True, font_weight='bold', pos=nx.spectral_layout(G))
# plt.show()
