#!/usr/bin/env python
# -*- coding: utf-8 -*-

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