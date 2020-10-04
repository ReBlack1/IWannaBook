#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_manager as bm
from lxml import etree
import re
from UDPipe_api import *
import networkx as nx
from scipy.spatial.distance import *
from training_manager import *
morph = pymorphy2.MorphAnalyzer()
import math



def add_to_graph(sintax, graph):
    sintax_dict = dict()
    sintax = sintax.split("\n")
    for word in sintax:
        if len(word) == 0 or word[0] == "#":
            continue
        word = word.replace("	", " ").split()
        if word[5] == "Foreign=Yes":  # текст не на русском
            return
        graph.add_node(word[2])
        sintax_dict[word[0]] = word[2]

    for word in sintax:
        if len(word) > 0 and word[0] != "#":
            word = word.replace("	", " ").split()
            if word[6] == "0":
                continue
            graph.add_edge(sintax_dict[word[6]], word[2], context=word[6])

def try1():
    G = nx.MultiGraph()

    path = r"test_books\1.zip"
    xml = bm.open_book(path)
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(xml)
    ans = _xpath(dom)

    for i in ans:
        """Обработка заголовков, автора и т.д. через i.text """
        if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
            """ Построчная обработка книги перед предпроцессингом (Только текста) """
            if not i.text:
                continue
            sintax = get_sintax(i.text)
            add_to_graph(sintax, G)

    keys = []
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)
    # for i in range(10):
    #     print(combined_model.make_sentence(tries=30))

    node_color = [G.degree(v)/10 for v in G]
    print(node_color)
    # node_size = [0.0005 * nx.get_node_attributes(G, 'population')[v] for v in G]
    nx.draw(G, nlist=[G.nodes], with_labels=True, node_color=node_color, font_color="k")
    plt.show()


def is_continue_word(word):
    if re.findall(r"[\W^ ]|[1-9]", word):
        return True
    if word in ["и", "в", "то", "что", "не", "как", "на", "из", "с", "а", "под", "только", "или", "еще", "да", "от",
                "у", "около", "но", "при", "же", "так", "если", "за", "который", "к", "те", "этот", "этого", "того",
                "чтобы  ", "чтоб", "бы", "по", "ли", "ну"]:
        return True
    if word in ["!", "..."]:
        return True
    if word in ["почти", "быть", "буду", "был", "была", "были"]:
        return True
    return False



def add_to_graph2(sintax, graph):
    sintax_dict = dict()  # Номер: слово, ссылка
    sintax = sintax.split("\n")
    for word in sintax:
        if len(word) == 0 or word[0] == "#":
            continue
        word = word.replace("	", " ").split()
        if word[5] == "Foreign=Yes":  # текст не на русском
            return
        graph.add_node(word[2])
        sintax_dict[word[0]] = word[2], word[6]

    for word in sintax:
        if len(word) > 0 and word[0] != "#":
            word = word.replace("	", " ").split()
            num_neib = word[6]  # Ссылка в лоб
            if num_neib == "0":  # Не ссылкается
                continue
            if is_continue_word(word[2]):  # Если текущее слово - проходное, пропустим
                continue

            if is_continue_word(sintax_dict[num_neib][0]):  # Если текущее слово ссылается на проходное, возьмем через одно
                num_neib = sintax_dict[num_neib][1]
                if num_neib == "0":
                    continue
            graph.add_edge(sintax_dict[num_neib][0], word[2], context=word[6])

def try2():
    G = nx.MultiGraph()

    path = r"test_books\slugi.zip"
    xml = bm.open_book(path)
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(xml)
    ans = _xpath(dom)

    for i in ans[599:600]:
        """Обработка заголовков, автора и т.д. через i.text """
        if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p

            """ Построчная обработка книги перед предпроцессингом (Только текста) """
            sintax = get_sintax(i.text)
            add_to_graph2(sintax, G)

    keys = []
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)
    # for i in range(10):
    #     print(combined_model.make_sentence(tries=30))

    node_color = [G.degree(v)*3 for v in G]
    # node_size = [0.0005 * nx.get_node_attributes(G, 'population')[v] for v in G]
    nx.draw(G, nlist=[G.nodes], with_labels=True, node_color=node_color, font_color="k")
    plt.show()


def create_sim_map(vec_list):
    size = len(vec_list)
    res_list = []
    for base in range(size):
        res_list.append([None]*size)
        for comp in range(base+1, size):
            res_list[base][comp] = cosine(vec_list[base], vec_list[comp])
    return res_list


def add_to_graph3(sintax, graph):
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
            if is_continue_word(word[2]):  # Если текущее слово - проходное, пропустим
                continue

            if is_continue_word(sintax_dict[num_neib][0]):  # Если текущее слово ссылается на проходное, возьмем через одно
                num_neib = sintax_dict[num_neib][1]
                if num_neib == "0":
                    continue
            graph.add_edge(sintax_dict[num_neib][0], word[2], context=word[6])


def replace_edge(node1, node2, new_node, graph):  # node1 ссылалась на node2 теперь будет на new_node
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


def copy_edge(node1, node2, new_node, graph):  # node1 ссылалась на node2 теперь будет на new_node
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


def combine_nodes(node1, node2, new_name, graph):
    sizes = nx.get_node_attributes(graph, "size")
    graph.add_node(new_name, size=sizes[node1]+sizes[node2])
    if new_name != node1:
        graph.add_edges_from([x for x in zip([new_name] * len(graph[node1]), graph[node1])])
        graph.remove_node(node1)
    if new_name != node2:
        graph.add_edges_from([x for x in zip([new_name] * len(graph[node2]), graph[node2])])
        graph.remove_node(node2)


def try3():
    G = nx.MultiGraph()

    path = r"test_books\slugi.zip"
    xml = bm.open_book(path)
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(xml)
    ans = _xpath(dom)

    for i in ans[599:600]:
        """Обработка заголовков, автора и т.д. через i.text """

        if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
            """ Построчная обработка книги перед предпроцессингом (Только текста) """
            sintax = get_sintax(i.text)
            add_to_graph3(sintax, G)

    keys = []
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)
    # for i in range(10):
    #     print(combined_model.make_sentence(tries=30))
    noun_word_list = []
    noun_vec_list = []
    verb_word_list = []
    verb_vec_list = []

    for word in G:  # Соберем вектора
        token_word = tokenizer.get_stat_token_word(morph, word)
        if token_word is None:
            continue
        vec = client.get_vec(token_word)
        if len(vec) == 0:
            continue

        if token_word.find("NOUN") != -1:  # Пока объединим только соществительные
            noun_word_list.append(word)
            noun_vec_list.append(vec)
        if token_word.find("VERB") != -1:  # Пока объединим только соществительные
            verb_word_list.append(word)
            verb_vec_list.append(vec)

    size = len(noun_vec_list)
    for base in range(size):
        for comp in range(base+1, size):
            if cosine(noun_vec_list[base], noun_vec_list[comp]) < 0.5:
                # print(noun_word_list[base], noun_word_list[comp])
                old_name1 = noun_word_list[base]
                old_name2 = noun_word_list[comp]
                if old_name1 == old_name2:
                    continue
                new_vec = (noun_vec_list[base] + noun_vec_list[comp]) / 2
                # print(new_vec)
                res = json.loads(client.get_word_by_vec(new_vec.tostring()).decode())["res"][0]
                new_name = res[0].split("_")[0]
                # print(new_name)
                # new_name = old_name1 + old_name2
                combine_nodes(old_name1, old_name2, new_name, G)
                for word in range(len(noun_word_list)):
                    if noun_word_list[word] in [old_name1, old_name2]:
                        noun_word_list[word] = new_name

    size = len(verb_vec_list)
    for base in range(size):
        for comp in range(base+1, size):
            if cosine(verb_vec_list[base], verb_vec_list[comp]) < 0.5:
                old_name1 = verb_word_list[base]
                old_name2 = verb_word_list[comp]
                if old_name1 == old_name2:
                    continue
                new_vec = (verb_vec_list[base] + verb_vec_list[comp]) / 2
                # print(new_vec)
                res = json.loads(client.get_word_by_vec(new_vec.tostring()).decode())["res"][0]
                new_name = res[0].split("_")[0]
                # new_name = old_name1 + old_name2
                combine_nodes(old_name1, old_name2, new_name, G)
                for word in range(len(verb_word_list)):
                    if verb_word_list[word] in [old_name1, old_name2]:
                        verb_word_list[word] = new_name

    keys = []
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)

    node_color = [G.degree(v)*3 for v in G]
    # print(G["я"])
    # for word in G["я"]:
    #     if len(G[word]) > 1:
    #         print(G[word])
    node_size = [400 * nx.get_node_attributes(G, 'size')[v] for v in G]
    print(nx.get_node_attributes(G, 'size'))
    nx.draw(G, nlist=[G.nodes], with_labels=True, node_color=node_color, font_color="k", node_size=node_size)
    plt.show()


def is_pronoun(word):
    return word in ["я", "ты", "он", "она", "вы", "мы", "этот", "тот", "они", "кто-то", "некто", "никто", "все", "это", "себя"]


def add_to_graph4(sintax, graph):
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
            if is_continue_word(word[2]):  # Если текущее слово - проходное, пропустим
                continue

            if is_continue_word(sintax_dict[num_neib][0]):  # Если текущее слово ссылается на проходное, возьмем через одно
                num_neib = sintax_dict[num_neib][1]
                if num_neib == "0":
                    continue
            graph.add_edge(sintax_dict[num_neib][0], word[2], context=word[6], story_time=len(graph.edges))



def try4():
    G = nx.MultiGraph()
    clf = train_logistic_regression(300, "person_train", const.person_list, const.non_person_list)

    path = r"test_books\slugi.zip"
    path = r"test_books\1.zip"

    xml = bm.open_book(path)
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(xml)
    ans = _xpath(dom)

    for i in ans:
        """Обработка заголовков, автора и т.д. через i.text """
        if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
            if not i.text:
                continue
            """ Построчная обработка книги перед предпроцессингом (Только текста) """
            sintax = get_sintax(i.text)
            add_to_graph4(sintax, G)

    # Граф собран - дальше постобработка

    keys = []  # Удалим вершины без ребер
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)

    # Обединим синонимы
    noun_word_list = []
    noun_vec_list = []
    verb_word_list = []
    verb_vec_list = []

    for word in G:  # Соберем вектора для объединения синонимов
        if is_pronoun(word):  # Метоимения не объединяем
            continue
        token_word = tokenizer.get_stat_token_word(morph, word)
        if token_word is None:
            continue
        vec = client.get_vec(token_word)
        if len(vec) == 0:
            continue

        if token_word.find("NOUN") != -1:  # Пока объединим только существительные
            noun_word_list.append(word)
            noun_vec_list.append(vec)
        if token_word.find("VERB") != -1:  # объединяем глаголы
            verb_word_list.append(word)
            verb_vec_list.append(vec)

    size = len(noun_vec_list)
    for base in range(size):  # Объединяем синонимы существительныз
        for comp in range(base+1, size):
            if cosine(noun_vec_list[base], noun_vec_list[comp]) < 0.5:
                old_name1 = noun_word_list[base]
                old_name2 = noun_word_list[comp]
                if old_name1 == old_name2:
                    continue
                new_vec = (noun_vec_list[base] + noun_vec_list[comp]) / 2
                res = json.loads(client.get_word_by_vec(new_vec.tostring()).decode())["res"][0]
                new_name = res[0].split("_")[0]
                combine_nodes(old_name1, old_name2, new_name, G)
                for word in range(len(noun_word_list)):
                    if noun_word_list[word] in [old_name1, old_name2]:
                        noun_word_list[word] = new_name

    size = len(verb_vec_list)
    for base in range(size):  # Объединяем синонимы глаголов
        for comp in range(base+1, size):
            if cosine(verb_vec_list[base], verb_vec_list[comp]) < 0.5:
                old_name1 = verb_word_list[base]
                old_name2 = verb_word_list[comp]
                if old_name1 == old_name2:
                    continue
                new_vec = (verb_vec_list[base] + verb_vec_list[comp]) / 2
                res = json.loads(client.get_word_by_vec(new_vec.tostring()).decode())["res"][0]
                new_name = res[0].split("_")[0]
                combine_nodes(old_name1, old_name2, new_name, G)
                for word in range(len(verb_word_list)):
                    if verb_word_list[word] in [old_name1, old_name2]:
                        verb_word_list[word] = new_name

    # убираем указательные местоимения
    target_pronouns = ["ты", "вы", "он", "она", "они"]
    story_hystory = nx.get_edge_attributes(G, "story_time")

    print(story_hystory)
    for pron in target_pronouns:  # Пробегаемся по местоимениям
        if pron not in G.nodes:
            continue

        pron_edges = list(G[pron].keys())
        for base_edge in pron_edges:  # берем все их связи
            if is_pronoun(base_edge) or is_continue_word(base_edge):  # Связи с проходными словами и метоимениями можно не учитывать
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
                    if is_pronoun(word):
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

                    dist = math.fabs(story_hystory[edge]-st_time)
                    if story_hystory[edge] < st_time:
                        dist /= 2
                    if min_person is None or dist < min_person:
                        min_person = math.fabs(story_hystory[edge]-st_time)
                        person = word
            replace_edge(pron, base_edge, person, G)

    for pron in target_pronouns:
        if pron in G.nodes:
            G.remove_node(pron)

    # i_do = G["я"].keys()
    # max_inter = 0
    # max_key = None
    # for key in G.nodes:
    #     if len(G[key].keys() & i_do)/len(G[key].keys() | i_do) > max_inter and not is_pronoun(key):
    #         max_key = key
    #         max_inter = len(G[key].keys() & i_do)/len(G[key].keys() | i_do)
#
    # print(max_key)
    # print((G[max_key].keys() & i_do))
    keys = []
    for key in G:
        if not G[key]:
            keys.append(key)
    for key in keys:
        G.remove_node(key)
    persons = []
    per_vec = []
    for node in G.nodes:
        token_word = tokenizer.get_stat_token_word(morph, node)
        if token_word is None or token_word.find("NOUN") == -1:
            continue
        vec = client.get_vec(token_word)
        if vec is None or len(vec) == 0:
            continue
        is_person = clf.predict(vec.reshape(1, -1))
        if is_person == 0:
            test_v = tokenizer.get_stat_token_word(morph, "налогоплательщик")
            test_vec = client.get_vec(test_v)
            print(node, cosine(test_vec, vec))

            persons.append(node)
            per_vec.append(vec)
    print("persons = ", persons)
    print()
    for i in persons:
        print(i)
    test_v = tokenizer.get_stat_token_word(morph, "налогоплательщик")
    test_vec = client.get_vec(test_v)
    s = 1
    for vec in per_vec:
        s *= cosine(test_vec, vec)
        print(cosine(test_vec, vec))
    s ** (1/len(persons))
    print(s)

    for per in persons:
        print(per, G[per])
    print()
    for per in G["человек"]:
        token_word = tokenizer.get_stat_token_word(morph, per)

        print(token_word)

    node_color = [(G.degree(v))*3 for v in G]
    node_size = [400 * nx.get_node_attributes(G, 'size')[v] for v in G]
     #print(nx.get_node_attributes(G, 'size'))
    nx.draw(G, nlist=[G.nodes], with_labels=True, node_color=node_color, font_color="k", node_size=node_size)
    plt.show()

# try1()
# try2()
# try3()
# heat_map_present()
try4()
exit()

