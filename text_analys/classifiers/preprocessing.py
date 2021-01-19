#!/usr/bin/env python
# -*- coding: utf-8 -*-

from text_analys.mining.tokenizer import Tokenizator
from text_analys.classifiers.training_manager import *
from text_analys.classifiers.const import *

tok = Tokenizator()
non_cruel_words = []
cruel_words = []
for word in cruel_word_list:
    cruel_words.append(tok.get_stat_token_word(word))
for word in non_cruel_word_list:
    non_cruel_words.append(tok.get_stat_token_word(word))
word_list = [non_cruel_words, cruel_words]
vector_dict, class_dict = create_word2vec_clf_dicts(word_list,
                                                    r"D:\Python\IWannaBook\text_analys\classifiers\dict\vec.plc",
                                                    r"D:\Python\IWannaBook\text_analys\classifiers\dict\class.plc")
train_w2v_logistic_regression(vector_dict, class_dict, r"D:\Python\IWannaBook\text_analys\classifiers\cruel_train.plc")
