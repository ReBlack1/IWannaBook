#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
from scipy.spatial.distance import cosine
# from training_manager import *
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
from graph_manager import merge_nodes
from word_manager import is_pronoun
from math_manager import cache_cosine, my_metric
import client
import tokenizer
CS = cache_cosine()


def combine_synonims(graph):
    voice_parts = ["NOUN", "VERB", "ADJ"]
    word_dict = {"NOUN": [], "VERB": [], "ADJ": []}
    for word in graph:  # Соберем вектора для объединения синонимов
        if is_pronoun(word):  # Метоимения не объединяем
            continue
        token_word = tokenizer.get_stat_token_word(morph, word)
        if token_word is None:
            graph.nodes[word]["token"] = None
            continue
        graph.nodes[word]["token"] = token_word
        vec = client.get_vec(token_word)
        if vec is None or not vec.any():
            graph.nodes[word]["vec"] = None
            continue
        graph.nodes[word]["vec"] = vec

        if token_word.find("NOUN") != -1:  # объединим только существительные
            word_dict["NOUN"].append(word)
        if token_word.find("VERB") != -1:  # объединяем глаголы
            word_dict["VERB"].append(word)
        if token_word.find("ADJ") != -1:  # объединяем прилагательные
            word_dict["ADJ"].append(word)

    for voice_part in voice_parts:
        word_list = word_dict[voice_part]
        size = len(word_list)
        for base in range(size):  # Объединяем синонимы существительныз
            for comp in range(base + 1, size):
                base_word = word_list[base]
                comp_word = word_list[comp]
                try:
                    base_vec = graph.nodes[base_word]["vec"]
                    comp_vec = graph.nodes[comp_word]["vec"]
                except KeyError:  # слово уже сравнивали и удалили
                    continue
                cos = cosine(base_vec, comp_vec)
                if cos < 0.5:
                    ans = merge_nodes(base_word, comp_word, graph)
                    if ans["res"]:
                        graph.nodes[base_word]["vec"] = (base_vec + comp_vec)/2
    return graph
