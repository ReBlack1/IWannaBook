#!/usr/bin/env python
# -*- coding: utf-8 -*-

from text_analys.classifiers.training_manager import *
from text_analys.classifiers.const import *


word_list = {"not cruel": non_cruel_word_list, "cruel": cruel_word_list}
train_w2v_logistic_regression(word_list, r"D:\Python\IWannaBook\text_analys\classifiers\cruel_train.plc")

# word_list = {"not sexual": non_sexual_word_list, "sexual": sexual_word_list}
# train_w2v_logistic_regression(word_list, r"D:\Python\IWannaBook\text_analys\classifiers\sexual_train.plc")

# word_list = {"not person": non_person_list, "person": person_list}
# train_w2v_logistic_regression(word_list, r"D:\Python\IWannaBook\text_analys\classifiers\person_train.plc")
