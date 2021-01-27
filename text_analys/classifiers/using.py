from text_analys.classifiers.classifier import *
import pickle
import networkx as nx
import book_manager
from lxml import etree
import re


def open_graph_from_plc(path):
    with open(path, 'rb') as f:
        graph = pickle.load(f)
    return graph


if __name__ == '__main__':
    path = r"D:\Python\IWannaBook\text_analys\classifiers\opt_graph_10001.plc"
    opt_graph = open_graph_from_plc(path)
    book_w_l = opt_graph['book_word_list']
    vectors = opt_graph['vectors']
    graph = opt_graph['graph']

    emotional_classifier = EmotionalClassifier()
    cruel_classifier = CruelClassifier()
    sexual_classifier = SexualClassifier()

    cnt_abstract = 0  # количество абстрактных слов
    cnt_all = 0  # количество всех слов
    vec_size = len(vectors)  # количество уникальных слов
    words_like = {}  # словарь со всеми словами, разбитыми на группы

    emotional_answer = emotional_classifier.predict_by_vectors(vectors)
    cruel_answer = cruel_classifier.predict_by_vectors(vectors)
    sexual_answer = sexual_classifier.predict_by_vectors(vectors)

    for i in range(vec_size):  # проходим по всем уникальным словам
        word = book_w_l[i]  # текущее слово
        cnt_word = graph.nodes[word]["size"]  # количество слов, синонимичных текущему
        cnt_all = cnt_all + cnt_word
        if word.split('_')[-1] in ['NOUN', 'VERB', 'ADJ', 'PRTF']:  # если слова важная часть речи
            emotional_appraisal = emotional_answer[i]
            cruel_appraisal = cruel_answer[i]
            sexual_appraisal = sexual_answer[i]
            if words_like.get(emotional_appraisal, None) is None:
                words_like[emotional_appraisal] = []
            if words_like.get(cruel_appraisal, None) is None:
                words_like[cruel_appraisal] = []
            if words_like.get(sexual_appraisal, None) is None:
                words_like[sexual_appraisal] = []
            words_like[emotional_appraisal].append((word, cnt_word))
            words_like[cruel_appraisal].append((word, cnt_word))
            words_like[sexual_appraisal].append((word, cnt_word))
    for word in words_like["abstract"]:
        cnt_abstract = cnt_abstract + word[1]
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
