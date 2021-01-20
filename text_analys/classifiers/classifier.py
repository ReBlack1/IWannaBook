#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import web_client.service_connector as client


class LogisticClassifier    :
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.person_classifier = pickle.load(f)

    def get_classifier_by_token(self, token):
        vec = client.get_vec(token).reshape((1, -1))
        if vec.size == 0:
            return None
        return self.person_classifier.predict(vec) == [1]


class PersonClassifier(LogisticClassifier):
    def __init__(self):
        path = r"D:\Python\IWannaBook\text_analys\classifiers\person_train.plc"
        super().__init__(path)


class CruelClassifier(LogisticClassifier):
    def __init__(self):
        path = r"D:\Python\IWannaBook\text_analys\classifiers\cruel_train.plc"
        super().__init__(path)


class SexualClassifier(LogisticClassifier):
    def __init__(self):
        path = r"D:\Python\IWannaBook\text_analys\classifiers\sexual_train.plc"
        super().__init__(path)

