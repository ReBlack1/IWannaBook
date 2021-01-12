#!/usr/bin/env python
# -*- coding: utf-8 -*-
from razdel import sentenize, tokenize
from navec import Navec
from slovnet import Syntax
from ipymarkup import show_dep_ascii_markup as show_markup  # Для красивого вывода синтаксиса

class SintaxisNavec:
    def __init__(self):
        self.navec = Navec.load('navec_news_v1_1B_250K_300d_100q.tar')
        self.syntax_parser = Syntax.load('slovnet_syntax_news_v1.tar')
        self.syntax_parser.navec(self.navec)

    def get_sintaxis(self, sentence):
        sintax_list = []
        chunk = []

        tokens = [_.text for _ in tokenize(sentence)]
        if tokens:
            chunk.append(tokens)
        syntax_map = self.syntax_parser.map(chunk)

        for markup in syntax_map:
            words, deps = [], []
            for token in markup.tokens:
                words.append(token.text)
                source = int(token.head_id) - 1
                target = int(token.id) - 1
                if source > 0 and source != target:  # skip root, loops
                    deps.append([source, target, token.rel])
            sintax_list.append((words, deps))

        return sintax_list[0]


# SN = SintaxisNavec()
# sintax = SN.get_sintaxis("Кем бы ты ни был, кем бы ты не стал, помни, где ты был и кем ты стал.")
# show_markup(sintax[0], sintax[1])
