import networkx as nx
import book_manager
from lxml import etree
import re
import math
from text_analys.classifiers.abstract_words import *
from image_manager.image_generator import text_on_picture


def preprocess_text(text):
    """
    Предпроцессинг текста:
    Замена url, замена ё на е, приведение в нижний регистр,
    Удаление знаков препинания,
    :param text:
    :return:
    """
    if text is None:
        return ""
    text = text.lower().replace("ё", "е")
    text = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+))', 'URL', text)
    text = re.sub(r'[^a-zA-Zа-яА-Я1-9]+', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


def find_best_abstract_sentence(book_path, graph_path):
    emotional_classifier = EmotionalClassifier()
    book_w_l, vectors, graph = get_all_about_graph(graph_path)
    abstract_list = find_abstract_list(graph, vectors, book_w_l, emotional_classifier)

    book_xml = book_manager.open_book(book_path)
    _xpath = etree.XPath(r'//*')
    dom = etree.XML(book_xml)
    ans = _xpath(dom)

    max_sentence_rating = 0
    cur_sentence_rating = 0
    best_sentence = ""
    for i in ans:
        """Обработка заголовков, автора и т.д. через i.text """
        if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
            if not i.text:  # Могут быть None
                continue
            for sentence in i.text.split("."):
                """ Построчная обработка книги перед предпроцессингом (Только текста) """
                sentence = preprocess_text(sentence)
                if not sentence:
                    continue
                sentence_word_list = sentence.split()
                cnt = 0
                for word_tok in abstract_list:
                    word = word_tok[0].split('_')[0]
                    cnt = cnt + sentence.count(word)
                znam = (len(sentence_word_list) - cnt)
                if cnt > 0 and znam != 0:
                    cur_sentence_rating = math.log10(len(sentence_word_list)) * cnt / znam
                    print(cur_sentence_rating, " : ", sentence)
                if cur_sentence_rating > max_sentence_rating:
                    max_sentence_rating = cur_sentence_rating
                    best_sentence = sentence
    print(max_sentence_rating)
    print(best_sentence)
    return best_sentence


if __name__ == '__main__':
    graph_path = r"D:\Python\IWannaBook\text_analys\classifiers\opt_graph_10019.plc"
    book_path = r"D:\Python\IWannaBook\test_books\flibusta_10019.zip"
    sentence = find_best_abstract_sentence(book_path, graph_path)

    best_img = text_on_picture(sentence)
    best_img.save("BEST.png", "png")