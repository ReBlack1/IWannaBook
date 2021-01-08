#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymorphy2

class Tokenizator:
    def __init__(self):
        self.stat_token_cache = dict()
        self.morph = pymorphy2.MorphAnalyzer()

    def get_stat_token_word(self, word):
        if self.stat_token_cache.get(word, None):
            return self.stat_token_cache[word]

        norm_word = self.morph.parse(word)[0]
        if norm_word is None or norm_word.tag.POS is None:
            self.stat_token_cache[word] = None
            return

        self.stat_token_cache[word] = norm_word.normal_form + "_" + correct_token(norm_word.tag.POS)
        return self.stat_token_cache[word]


def correct_token(token):
    if token in ["ADJS", "ADJF", "COMP"]:
        return "ADJ"
    if token in ["NPRO"]:
        return "NOUN"
    if token in ["PRCL", "ADVB", "CONJ"]:
        return "ADV"
    if token in ["PREP"]:
        return "PROPN"
    if token in ["INFN"]:
        return "VERB"
    return token


def get_stat_token_word(morph, word):
    norm_word = morph.parse(word)[0]
    if norm_word is None or norm_word.tag.POS is None:
        return
    return norm_word.normal_form + "_" + correct_token(norm_word.tag.POS)
