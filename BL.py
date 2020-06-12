#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import UDPipe_api
import pymorphy2
import tokenizer
from training_manager import *
import const
import client
import text_to_graph


def find_book_by_desc(desc):
    G = text_to_graph.request_to_graph(desc)
    morph = pymorphy2.MorphAnalyzer()

    print(G)
    persons = []
    clf = train_logistic_regression(300, "person_train", const.person_list, const.non_person_list)
    for word in G.nodes:
        token_word = tokenizer.get_stat_token_word(morph, word)
        if not token_word:
            continue
        vec = client.get_vec(token_word)
        if vec is None or len(vec) == 0:
            continue
        is_person = clf.predict(vec.reshape(1, -1))
        if is_person == 0:
            persons.append(word)
    print(persons)
    for per_desk in persons:
        print(G[per_desk])
