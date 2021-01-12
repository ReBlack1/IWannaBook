#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import web_client.service_connector as client


class PersonClassifier:
    def __init__(self):
        with open(r'D:\py_projects\IWonnaBook\classifiers\person_train.plc', 'rb') as f:
            self.person_classifier = pickle.load(f)

    def get_classifier_by_token(self, token):
        vec = client.get_vec(token).reshape((1, -1))
        if vec.size == 0:
            return None
        return self.person_classifier.predict(vec) == [1]

