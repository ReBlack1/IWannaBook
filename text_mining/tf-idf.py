#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
from collections import Counter
import math
import pickle

def compute_tfidf(corpus):
    """
    Определяет TF-IDF
    """
    tf_list = []
    idf_dict = {}
    for line in corpus:
        text = line.split()
        tf_text = Counter(text)  # Словарь {Слово: кол-во}

        for key in tf_text:
            if idf_dict.get(key, None):
                idf_dict[key] += 1
            else:
                idf_dict[key] = 1
            # Считаем tf
            tf_text[key] = tf_text[key] / len(text)
        tf_list.append(tf_text)

    # Считаем idf
    corpus_len = len(corpus)
    for word in idf_dict:
        idf_dict[word] = math.log10(corpus_len / idf_dict[word])

    # Перемножаем
    for tf_text in tf_list:
        for word in tf_text:
            weight = tf_text[word] * idf_dict[word]
            tf_text[word] = weight

    return tf_list

with open("clear_material/nered_rejects.pkl", 'rb') as f:
    corpus = pickle.load(f)

compute_list = compute_tfidf(corpus)

with open("clear_material/compute_list_full.pkl", 'wb') as f:
   pickle.dump(compute_list, f)

