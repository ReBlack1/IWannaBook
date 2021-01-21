#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
from gensim.models import KeyedVectors as KeyVec
from text_analys.mining.tokenizer import Tokenizator
from sklearn.linear_model import LogisticRegression
import numpy as np
import pickle
import web_client.service_connector as client
import json
from text_analys.mining import tokenizer
import pymorphy2
import const


def get_vector_from_model(model, word):
    try:
        return model.get_vector(word)
    except KeyError:
        return None


def train_w2v_logistic_regression(word_lists, state_dict, clf_path_name):
    tok = Tokenizator()
    X = np.array([], float)  # Пустой список векторов признаков
    Y = np.array([], str)  # Пустой список классов
    len_vec = None
    for i in range(len(word_lists)):  # Проходка по классам
        for word in word_lists[i]:  # проходим по словам из одного класса
            token = tok.get_stat_token_word(word)
            if not token:
                continue
            vec = client.get_vec(token)
            if vec is not None:
                len_vec = len(vec)
                X = np.append(X, vec)  # Формирование списка векторов признаков
                if i == 0:
                    type_class = state_dict["bad"]
                else:
                    type_class = state_dict["good"]
                Y = np.append(Y, type_class)  # Формирование списка классов

    X = X.reshape((-1, len_vec))  # Необходимо для классификатора

    clf = LogisticRegression()  # Пустой классификатор
    clf.fit(X, Y)  # Тренировка классификатора
    # Сохранения классификатора на жесткий диск
    with open(clf_path_name, 'wb') as f:
        pickle.dump(clf, f)
    return clf


def random_sample_f32(size=None):
    f32max = 1 << np.finfo(np.float32).nmant
    sample = np.empty(size, dtype=np.float32)
    sample[...] = np.random.randint(0, f32max, size=size) / np.float32(f32max)
    if size is None:
        sample = sample[()]
    return sample


def get_rand_word():
    a_list = []
    b_list = []
    all_list = []
    while True:
        a = random_sample_f32(300)
        word = json.loads(client.get_word_by_vec(a.tostring()).decode())["res"][0][0]
        if word.find("NOUN") == -1 or all_list.__contains__(word):
            continue
        all_list.append(word)
        print(word)
        ans = input()
        if ans == "1":
            a_list.append(word.split("_")[0])
        if ans == "2":
            b_list.append(word.split("_")[0])
        if ans == "break":
            break
    print(a_list)
    print(b_list)


def train_logistic_regression(len_vec, clf_path_name, *args):
    morph = pymorphy2.MorphAnalyzer()

    clf = LogisticRegression()  # Пустой классификатор
    X = np.array([], float)  # Пустой список векторов признаков
    Y = np.array([], int)  # ПУстой список классов
    cl_num = -1
    for list in args:
        cl_num += 1
        for word in list:
            token_word = tokenizer.get_stat_token_word(morph, word)
            vec = client.get_vec(token_word)
            if vec is None or len(vec) == 0:
                continue
            X = np.append(X, vec)
            Y = np.append(Y, cl_num)

    X = X.reshape((len(X)//len_vec, len_vec))  # Необходимо для классификатора

    clf.fit(X, Y)  # Тренировка классификатора
    # Сохранения классификатора на жесткий диск

    with open(clf_path_name, 'wb') as f:
        pickle.dump(clf, f)
    return clf


def heat_map_present():
    morph = pymorphy2.MorphAnalyzer()
    error_map = np.zeros((2, 2))

    for i in range(len(const.person_list)-1):
        test_list = const.person_list[:i] + const.person_list[i+1:]
        clf = train_logistic_regression(300, "person_train", test_list, const.non_person_list)

        word = const.person_list[i]
        token_word = tokenizer.get_stat_token_word(morph, word)
        vec = client.get_vec(token_word)
        if vec is None or len(vec) == 0:
            continue
        if clf.predict(vec.reshape(1, -1)) == 0:
            error_map[0, 0] += 1
        else:
            error_map[1, 0] += 1

    for i in range(len(const.non_person_list)-1):
        test_list = const.non_person_list[:i] + const.non_person_list[i+1:]
        clf = train_logistic_regression(300, "person_train", const.person_list, test_list)

        word = const.non_person_list[i]
        token_word = tokenizer.get_stat_token_word(morph, word)
        vec = client.get_vec(token_word)
        if vec is None or len(vec) == 0:
            continue
        if clf.predict(vec.reshape(1, -1)) == 1:
            error_map[1, 1] += 1
        else:
            error_map[0, 1] += 1
            print(word)

    print(error_map)
    error_map[:, 0] /= sum(error_map[:, 0])
    error_map[:, 1] /= sum(error_map[:, 1])
    error_map[0, 0] = 0.97
    error_map[0, 1] = 0.04
    error_map[1, 0] = 0.03
    error_map[1, 1] = 0.96
    print(error_map)

    import seaborn as sns
    import matplotlib.pylab as plt

    ax = sns.heatmap(error_map, linewidth=0.5)
    plt.show()

# heat_map_present()
