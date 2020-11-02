#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import text_to_graph
import book_manager as bm
from lxml import etree
import re
from language_tools.UDPipe_api import *
import networkx as nx
import math
from graph_manager import add_to_graph, replace_edge
from base_analys.word_manager import is_pronoun, is_continue_word
import time
from book_processing import combine_synonims
from language_tools import udpipe
import pickle
import pymorphy2
import tokenizer
import const
import client
from training_manager import train_logistic_regression


def find_book_by_desc(desc):
    G = text_to_graph.request_to_graph(desc)
    morph = pymorphy2.MorphAnalyzer()

    print(G)
    persons = []
    with open(r"person_train.plc", 'r') as f:
        clf = pickle.load(f)  # train_logistic_regression(300, "person_train", const.non_person_list, const.person_list)
    for word in G.nodes:
        token_word = tokenizer.get_stat_token_word(morph, word)
        if not token_word:
            continue
        vec = client.get_vec(token_word)
        if vec is None or len(vec) == 0:
            continue
        is_person = clf.predict(vec.reshape(1, -1))
        if is_person == 0:
            persons.append(word)
    print(persons)
    for per_desk in persons:
        print(G[per_desk])


def delete_target_pronouns(graph):
    with open(r"person_train.plc", 'rb') as f:
        clf = pickle.load(f)  # train_logistic_regression(300, "person_train", const.non_person_list, const.person_list)

    # убираем указательные местоимения
    target_pronouns = ["ты", "вы", "он", "она", "они"]
    story_hystory = nx.get_edge_attributes(graph, "story_time")

    for pron in target_pronouns:  # Пробегаемся по местоимениям
        if pron not in graph.nodes:
            continue

        pron_edges = list(graph[pron].keys())
        for base_edge in pron_edges:  # берем все их связи
            if is_pronoun(base_edge) or is_continue_word(
                    base_edge):  # Связи с проходными словами и метоимениями можно не учитывать
                continue
            min_person = None
            person = None

            st_time = None  # Ищем момент сюжета (по идее надо для каждого момента в сюжете повторить)
            if (pron, base_edge, 0) in story_hystory.keys():
                st_time = story_hystory[(pron, base_edge, 0)]
            if (base_edge, pron, 0) in story_hystory.keys():
                st_time = story_hystory[(base_edge, pron, 0)]
            if st_time is None:
                continue

            for edge in story_hystory:  # Ищем ближайшего персонажа к данному
                token_word = graph.nodes[edge[1]].get("token", None)  # tokenizer.get_stat_token_word(morph, base_edge)
                if token_word is None or token_word.find("NOUN") == -1:
                    continue
                vec = graph.nodes[edge[1]].get("vec", None)  # client.get_vec(token_word)
                if vec is None:
                    continue
                is_person = clf.predict(vec.reshape(1, -1))
                if not is_person:
                    continue

                dist = math.fabs(story_hystory[edge] - st_time)
                if story_hystory[edge] < st_time:
                    dist /= 2
                if min_person is None or dist < min_person:
                    min_person = math.fabs(story_hystory[edge] - st_time)
                    person = base_edge
            replace_edge(pron, base_edge, person, graph)

    for pron in target_pronouns:
        if pron in graph.nodes:
            graph.remove_node(pron)

    return graph


def compress_book(path):
    UD = udpipe.UDPipe()
    G = nx.MultiGraph()

    xml = bm.open_book(path)
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(xml)
    ans = _xpath(dom)

    author = dict()
    book_title = None

    sintax_time = time.time()
    # Создаем первичный граф
    for i in ans[:100]:  # TODO Распаралелить?
        """Обработка заголовков, автора и т.д. через i.text """
        if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
            if not i.text:
                continue
            """ Построчная обработка книги перед предпроцессингом (Только текста) """
            text_list = i.text.split(". ")
            for text in text_list:
                sintax = UD.get_sintax(text)
                add_to_graph(sintax, G)
        else:
            if re.search(r"\blast-name", i.tag) and author.get('last', None) is None:
                author["last"] = i.text
            if re.search(r"\bmiddle-name", i.tag) and author.get('middle', None) is None:
                author["middle"] = i.text
            if re.search(r"\bfirst-name", i.tag) and author.get('first', None) is None:
                author["first"] = i.text
            if re.search(r"\bbook-title", i.tag) and book_title is None:
                book_title = i.text

    print(book_title)
    author_str = author.get('last', "")
    if author_str:
        if author.get('first', ""):
            author_str += ' ' + author['first'][:1].upper() + "."
            if author.get('middle', ""):
                author_str += author['middle'][:1].upper() + "."
    print(author_str)
    print("Время обработки синтаксиса из {} равно {}".format(str(len(ans)), str(time.time() - sintax_time)))
    # with open(r"sintax_models\slugi_sintax_dict.plk", 'wb') as f:
    #     pickle.dump(sintax_dict, f)
    # Граф собран - дальше постобработка
    # Объединим синонимы
    sintax_time = time.time()

    G = combine_synonims(G)
    print("Время обработки синонимов для {} равно {}".format(str(len(G)), str(time.time() - sintax_time)))

    # убираем указательные местоимения
    sintax_time = time.time()
    G = delete_target_pronouns(G)
    print("Время обработки местоимений для {} равно {}".format(str(len(G)), str(time.time() - sintax_time)))

    # Удаляем одинокие вершины
    keys = []
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)

    return {"book_title": book_title, "author": author_str, "graph": G}


def make_scene(graph):
    person_clf = train_logistic_regression(300, "person_train", const.non_person_list, const.person_list)
    do_clf = train_logistic_regression(300, "do_train", const.state_list, const.do_list)
    sizes = nx.get_node_attributes(graph, 'size')
    morph = pymorphy2.MorphAnalyzer()

    book_scene = {"persons": [], "person_adjs": [], "decoration": [], "decoration_adjs": [], "do": [], "state": []}

    for node in graph:
        token_word = tokenizer.get_stat_token_word(morph, node)
        if token_word is None:
            continue
        vec = client.get_vec(token_word)
        if vec is None or len(vec) == 0:
            continue

        if token_word.find("NOUN") != -1:  # Обработка существительных
            is_person = person_clf.predict(vec.reshape(1, -1))
            if is_person:
                book_scene["persons"].append({"name": node, "vec": vec})
            else:
                book_scene["decoration"].append({"name": node, "vec": vec})

            for edge in graph[node]:
                token_edge = tokenizer.get_stat_token_word(morph, edge)
                if token_edge is None or token_edge[-3:] not in ["ERB", "ADJ"]:
                    continue
                edge_vec = client.get_vec(token_edge)
                if edge_vec is None or len(edge_vec) == 0:
                    continue
                if is_person:
                    book_scene["person_adjs"].append({"name": edge, "vec": edge_vec})
                else:
                    book_scene["decoration_adjs"].append({"name": edge, "vec": edge_vec})
        if token_word.find("VERB") != -1:  # Обработка глаголов
            is_active = do_clf.predict(vec.reshape(1, -1))
            if is_active:
                book_scene["do"].append({"name": node, "vec": vec})
            else:
                book_scene["state"].append({"name": node, "vec": vec})


    scene = dict()
    for tp in book_scene.keys():
        obj_count = 0
        obj_vec = None
        for obj in book_scene[tp]:
            # print(person["name"], end=" ")
            if obj_vec is None:
                obj_vec = obj["vec"] * sizes[obj["name"]]
            else:
                obj_vec = obj["vec"] * sizes[obj["name"]] + obj_vec

            obj_count += sizes[obj["name"]]
        if obj_vec is None or obj_count == 0:
            scene[tp + "_vec"] = ""
            scene[tp + "_name"] = ""
            continue
        obj_vec = obj_vec / obj_count
        scene[tp + "_vec"] = obj_vec
        scene[tp + "_name"] = json.loads(client.get_word_by_vec(obj_vec.tostring()).decode())["res"][0]

    print("Средний персонаж ", scene["persons_name"])

    print("Средний описание персонаж ", scene["person_adjs_name"])

    print("Средняя декорация", scene["decoration_name"])

    print("Среднее описание декорации", scene["decoration_adjs_name"])

    print("Среднее дело ", scene["do_name"])

    print("Среднее изменение состояния ", scene["state_name"])

    return scene

