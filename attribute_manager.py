#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import re, string
import book_manager as bm
import pymorphy2
from lxml import etree, objectify
import sqlite_manager as sqlite
import time
from collections import Counter
import visualization as vis


class AttributeManager:
    morph = pymorphy2.MorphAnalyzer()
    book_strings = None
    counter = None
    swear_set = set()

    _avd_quantity = 100
    avd_word_counter = 0
    verb_now = 0
    noun_now = 0
    verb_list = []
    noun_list = []
    adv_now = 0
    adv_list = []

    def new_book_analys(self, path):
        """Обнуление переменных на случай, если была загружена прошлая книга"""
        self.book_strings = []
        self.counter = Counter([])
        self.swear_set = set()

        self.avd_word_counter = 0
        self.verb_now = 0
        self.noun_now = 0
        self.adv_now = 0
        self.verb_list = []
        self.noun_list = []
        self.adv_list = []

        xml = bm.open_book(path)
        _xpath = etree.XPath(r'//*')
        dom = etree.XML(xml)
        ans = _xpath(dom)
        for i in ans[:200]:
            """Обработка заголовков, автора и т.д. через i.text """
            if re.search(r"\b[p]", i.tag):  # предполагаю, что строки с текстом заканчиваются на p
                """ Построчная обработка книги перед предпроцессингом (Только текста) """
                p_text = self.preprocess_text(i.text)  # Обработка каждой строки книги
                """ Построчная обработка после предпроцессинга (Только текста)"""
                self.get_structure(p_text)
        # print(self.counter)
        """ Работа с вторичными данными"""
        self.swear_set = self.swear_counter(self.counter)
        x_plt = [i for i in range(self._avd_quantity, len(self.noun_list)*self._avd_quantity+1, self._avd_quantity)]
        plt = vis.f_plot(x_plt, self.noun_list, x_plt, self.verb_list, x_plt, self.adv_list, colors=["red", "green", "blue"], plot_names=['Сущ.', 'Глаголы', "Прил."])
        plt.show()

        # print(self.swear_set)

    @staticmethod
    def preprocess_text(self, text):
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

    def get_structure(self, line):
        """
        Составление словаря частотности слов
        :param line: строка из книги после предпроцессинга
        :return:
        """
        temp_list = []
        for word in line.split():  # Вся обработка нормализованных слов здесь
            """ Проверка слова на часть речи"""
            if self.morph.parse(word)[0].tag.POS == 'NOUN':
                self.noun_now += 1
            if self.morph.parse(word)[0].tag.POS == 'VERB' or self.morph.parse(word)[0].tag.POS == 'INFN':
                self.verb_now += 1
            if self.morph.parse(word)[0].tag.POS == 'ADJF' or self.morph.parse(word)[0].tag.POS == 'ADJS':
                self.adv_now += 1
            self.avd_word_counter += 1
            if self.avd_word_counter >= self._avd_quantity:
                self.verb_list.append(self.verb_now)
                self.noun_list.append(self.noun_now)
                self.adv_list.append(self.adv_now)
                self.verb_now, self.noun_now, self.adv_now, self.avd_word_counter = 0, 0, 0, 0
            normal_word = self.morph.normal_forms(word)[0]
            temp_list.append(normal_word)
        # print(temp_list)
        self.counter.update(temp_list)  # Сосавление словаря частотности

    @staticmethod
    def swear_counter(counter):
        """
        Поиск бранных слов из словаря частотности
        :counter: экземпляр collections.Counter с частотностью слов
        :return: множество бранных слов из словаря частотности (кол-во можно получить через словарь частотности)
        """
        _mats = {r'(ху(й|е|ё|и|я|ли[^а-я])\w*)',
                 r'(п(и|е|ё)(з|с)д)\w*',
                 r'([^а-я])(би?ля(д|т|[^а-я]))\w*',
                 r'(пид(о|а)р|п(е|и)дри)\w*',
                 r'(муд(ак|ач|о|и))\w*',
                 r'(([^а-я]|по|на|от|не|ни)(х|x)(е|e)(р|p))\w*',
                 r'(з(а|о)луп(а|и))\w*',
                 r'(([^а-я]у?|под?|на|за|от|вы|ь|ъ)(е|ё|и)б(а|ыр|у|нут|ись|ище))\w*',
                 r'([^а-я])((на|по)х)([^а-я])\w*'
                 r'(су(ка|чк|ки|чь))\w*',
                 r'(др(оч|ачи))\w*',
                 r'((\W|о|за)трах)\w*'}
        swear_set = set()
        for word in counter.keys():  # слова - ключи от словаря частотности
            for reg in _mats:  # перебор регулярок с шаблонами матов
                if re.search(reg, word):
                    swear_set.add(word)  # сохранение в множество класса
        return swear_set


conn = sqlite.get_connection(r"D:\Kursovaya\BookDB.db")
id_loading_book_list = sqlite.get_id_loading_book(conn)

BA = AttributeManager()
st = time.time()
BA.new_book_analys(r"D:\Kursovaya\books\159352.zip")
print(time.time() - st)

