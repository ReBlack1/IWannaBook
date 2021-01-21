#!/usr/bin/env python
# -*- coding: utf-8 -*-

from text_analys.classifiers.training_manager import *
from text_analys.classifiers.const import *


word_list = [non_cruel_word_list, cruel_word_list]
state_dict = {"good": "cruel", "bad": "not cruel"}
train_w2v_logistic_regression(word_list, state_dict, r"D:\Python\IWannaBook\text_analys\classifiers\cruel_train.plc")
