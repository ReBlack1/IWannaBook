#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymorphy2


class SentenceMaker:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.schemes = {
            ("NOUN", "VERB", "NOUN"): {"forms": [{'sing', 'nomn'}, {'3per', 'sing'}, {'sing', 'accs'}],
                                       "format_string": "{0} {1} {2}."}
        }

    def make_sentence(self, token_list):
        sentence_list = []
        tokens = []
        for token_word in token_list:
            token = token_word.split("_")[1]
            tokens.append(token)

        scheme = self.schemes[tuple(tokens)]["forms"]
        format_string = self.schemes[tuple(tokens)]["format_string"]

        for word_num in range(len(token_list)):
            word = token_list[word_num].split("_")[0]
            parsed_word = self.morph.parse(word)[0]
            formated_word = parsed_word.inflect(scheme[word_num])
            if formated_word is None:
                print(parsed_word, "is None")
                return None
            sentence_list.append(formated_word.word)
        print(format_string.format(*tuple(sentence_list)))


# a = 'учиться'
# word = morph.parse(a)[0]
# w = word.inflect({'3per','sing'}).word
# print(w)
a = SentenceMaker()
b = ['мальчик_NOUN', 'прижать_VERB', 'нога_NOUN']
a.make_sentence(b)

