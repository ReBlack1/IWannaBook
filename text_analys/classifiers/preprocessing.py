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
train_w2v_logistic_regression(word_list, r"D:\Python\IWannaBook\text_analys\classifiers\cruel_train.plc")
