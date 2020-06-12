#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import pickle
import pymorphy2


class WordClassifier:
    pass


def get_vector_from_model(model, word):
    try:
        return model.get_vector(word)
    except KeyError:
        return None


def get_object_from_plc(plc_path):
    obj = None
    with open(plc_path, 'rb') as f:
        obj = pickle.load(f)
    return obj
