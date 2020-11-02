#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from language_tools.UDPipe_api import *
import networkx as nx
import client
import pymorphy2
import tokenizer
# from training_manager import *
import math
import pickle


def __is_continue_word(word):
    if re.findall(r"[\W^ ]|[1-9]", word):
        return True
    if word in ["и", "в", "то", "что", "не", "как", "на", "из", "с", "а", "под", "только", "или", "еще", "да", "от",
                "у", "около", "но", "при", "же", "так", "если", "за", "который", "к", "те", "этот", "этого", "того",
                "чтобы", "чтоб", "бы", "по", "ли", "ну"]:
        return True
    if word in ["!"]:
        return True
    return False


def __is_pronoun(word):
    return word in ["я", "ты", "он", "она", "вы", "мы", "этот", "тот", "они", "кто-то", "некто", "никто", "все", "это", "себя"]


def __add_to_graph(sintax, graph):
    sintax_dict = dict()  # Номер: слово, ссылка
    sintax = sintax.split("\n")

    for word in sintax:  # Добавляем вершины
        if len(word) == 0 or word[0] == "#":
            continue
        word = word.replace("	", " ").split()
        if word[5] == "Foreign=Yes":  # текст не на русском
            return
        if word[2] in graph.nodes.keys():
            sizes = nx.get_node_attributes(graph, "size")
            sizes[word[2]] += 1
        else:
            graph.add_node(word[2], size=1)
        sintax_dict[word[0]] = word[2], word[6]

    for word in sintax:  # Добавляем ребра
        if len(word) > 0 and word[0] != "#":
            word = word.replace("	", " ").split()
            num_neib = word[6]  # Ссылка в лоб
            if num_neib == "0":  # Не ссылкается
                continue
            if __is_continue_word(word[2]):  # Если текущее слово - проходное, пропустим
                continue

            if __is_continue_word(sintax_dict[num_neib][0]):  # Если текущее слово ссылается на проходное, возьмем через одно
                num_neib = sintax_dict[num_neib][1]
                if num_neib == "0":
                    continue
            graph.add_edge(sintax_dict[num_neib][0], word[2], context=word[6], story_time=len(graph.edges))


def __replace_edge(node1, node2, new_node, graph):  # node1 ссылалась на node2 теперь будет на new_node
    hystory = nx.get_edge_attributes(graph, "story_time")
    story_time = None
    for i in range(10000):
        if (node1, node2, i) in hystory.keys():
            story_time = hystory[(node1, node2, i)]
        if (node2, node1, i) in hystory.keys():
            story_time = hystory[(node2, node1, i)]
    graph.remove_edge(node1, node2)
    if story_time is None:
        return
    graph.add_edge(node1, new_node, story_time=story_time)


def __copy_edge(node1, node2, new_node, graph):  # node1 ссылалась на node2 теперь будет на new_node
    hystory = nx.get_edge_attributes(graph, "story_time")
    story_time = None
    for i in range(10000):
        if (node1, node2, i) in hystory.keys():
            story_time = hystory[(node1, node2, i)]
        if (node2, node1, i) in hystory.keys():
            story_time = hystory[(node2, node1, i)]
    if story_time is None:
        return
    graph.add_edge(node1, new_node, story_time=story_time)


def __combine_nodes(node1, node2, new_name, graph):
    sizes = nx.get_node_attributes(graph, "size")
    graph.add_node(new_name, size=sizes[node1]+sizes[node2])
    if new_name != node1:
        graph.add_edges_from([x for x in zip([new_name] * len(graph[node1]), graph[node1])])
        graph.remove_node(node1)
    if new_name != node2:
        graph.add_edges_from([x for x in zip([new_name] * len(graph[node2]), graph[node2])])
        graph.remove_node(node2)


def request_to_graph(text):
    G = nx.MultiGraph()
    morph = pymorphy2.MorphAnalyzer()

    # clf = train_logistic_regression(300, "person_train", const.person_list, const.non_person_list)
    with open(r"person_train", 'r') as f:
        clf = pickle.load(f)  # train_logistic_regression(300, "person_train", const.non_person_list, const.person_list)

    sintax = get_sintax(text)
    __add_to_graph(sintax, G)

    # Граф собран - дальше постобработка
    keys = []  # Удалим вершины без ребер
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)

    # убираем указательные местоимения
    target_pronouns = ["ты", "вы", "он", "она", "они"]
    story_hystory = nx.get_edge_attributes(G, "story_time")

    print(story_hystory)
    for pron in target_pronouns:  # Пробегаемся по местоимениям
        if pron not in G.nodes:
            continue

        pron_edges = list(G[pron].keys())
        for base_edge in pron_edges:  # берем все их связи
            if __is_pronoun(base_edge) or __is_continue_word(
                    base_edge):  # Связи с проходными словами и метоимениями можно не учитывать
                continue
            min_person = None
            person = None

            st_time = None
            for q in range(10000):
                if (pron, base_edge, q) in story_hystory.keys():
                    st_time = story_hystory[(pron, base_edge, q)]
                if (base_edge, pron, q) in story_hystory.keys():
                    st_time = story_hystory[(base_edge, pron, q)]
                if st_time is not None:
                    break
            if st_time is None:
                # print(G[base_edge])
                # for line in story_hystory:  # Когда объединяли синонимы - мы выкидывали время в сюжете
                #     if line[0] == base_edge or line[1] == base_edge:
                #         print(line)
                continue

            for edge in story_hystory:  # Ищем ближайшего персонажа к данному
                for word in edge[:2]:
                    if __is_pronoun(word):
                        continue
                    token_word = tokenizer.get_stat_token_word(morph, word)
                    if token_word is None or token_word.find("NOUN") == -1:
                        continue
                    vec = client.get_vec(token_word)
                    if vec is None or len(vec) == 0:
                        continue
                    is_person = clf.predict(vec.reshape(1, -1))
                    if is_person != 0:
                        continue

                    dist = math.fabs(story_hystory[edge] - st_time)
                    if story_hystory[edge] < st_time:
                        dist /= 2
                    if min_person is None or dist < min_person:
                        min_person = math.fabs(story_hystory[edge] - st_time)
                        person = word
            __replace_edge(pron, base_edge, person, G)

    for pron in target_pronouns:
        if pron in G.nodes:
            G.remove_node(pron)

    keys = []
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)

    return G

