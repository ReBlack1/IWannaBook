from text_analys.classifiers.classifier import *
import pickle
import time
import networkx as nx
import book_manager
from lxml import etree
import re


def open_graph_from_plc(path):
    with open(path, 'rb') as f:
        graph = pickle.load(f)
    return graph


def find_abstract_list(graph, vectors, book_w_l, emotional_classifier):
    vec_size = len(vectors)  # количество уникальных слов
    abstract_words = []
    emotional_answer = emotional_classifier.predict_by_vectors(vectors)
    for i in range(vec_size):  # проходим по всем уникальным словам
        word = book_w_l[i]  # текущее слово
        if word.split('_')[-1] in ['NOUN', 'VERB', 'ADJ', 'PRTF']:  # если слова важная часть речи
            if emotional_answer[i] == "abstract":
                cnt_word = graph.nodes[word]["size"]  # количество слов, синонимичных текущему
                abstract_words.append((word, cnt_word))
    return abstract_words


def find_cnt_all_words(graph, vectors, book_w_l):
    vec_size = len(vectors)  # количество уникальных слов
    cnt_all = 0
    for i in range(vec_size):  # проходим по всем уникальным словам
        word = book_w_l[i]  # текущее слово
        cnt_all = cnt_all + graph.nodes[word]["size"]  # количество слов, синонимичных текущему
    return cnt_all

if __name__ == '__main__':
    emotional_classifier = EmotionalClassifier()

    start = time.time()

    path = r"D:\Python\IWannaBook\text_analys\classifiers\opt_graph_10019.plc"
    opt_graph = open_graph_from_plc(path)
    book_w_l = opt_graph['book_word_list']
    vectors = opt_graph['vectors']
    graph = opt_graph['graph']

    abstract_word_list = find_abstract_list(graph, vectors, book_w_l, emotional_classifier)
    cnt_all = find_cnt_all_words(graph, vectors, book_w_l)
    cnt_abstract = 0  # количество абстрактных слов
    for word in abstract_word_list:
        cnt_abstract = cnt_abstract + word[1]

    end = time.time()

    print(end - start)
    print('Абстрактных слов: ', cnt_abstract)
    print('Всего слов: ', cnt_all)
    print('Книга абстрактна на ', str('{:.2f}'.format(cnt_abstract / cnt_all)))

    # # поиск предложений в книге
    # # найти предложение с максимальным количеством абстрактных слов
    # book_xml = book_manager.open_book(book_path)
    # _xpath = etree.XPath(r'//*')
    # dom = etree.XML(book_xml)
    # ans = _xpath(dom)
    #
    # sintax_list = []
    # chunk = []
    #
    # for i in ans:
    #     """Обработка заголовков, автора и т.д. через i.text """
    #     if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
    #         if not i.text:  # Могут быть None
    #             continue
    #         for sentence in i.text.split("."):
    #             """ Построчная обработка книги перед предпроцессингом (Только текста) """
    #             if not sentence:
    #                 continue
