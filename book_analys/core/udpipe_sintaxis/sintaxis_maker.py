#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_manager
import zipfile
from lxml import etree
from language_tools.udpipe import UDPipe
import pickle
from base_analys.base_helper import get_base_info_from_book_xml, get_sintax_list
import config

if __name__ == '__main__':
    udpipe = UDPipe()
    for book_num in range(11431, 15000):
        book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'
        try:
            book_xml = book_manager.open_book(book_path)
            book_info = get_base_info_from_book_xml(book_xml)
            print(book_num, book_info)
            sintax_list = get_sintax_list(udpipe, book_xml)
            sintax_save_path = config.sintax_path + r"\sintax_flibusta_" + str(book_num) + '.plc'
            with open(sintax_save_path, 'wb') as f:
                clf = pickle.dump(sintax_list, f)
                print("Сохранено :) ")
        except zipfile.BadZipFile:
            # book = open(book_path, 'r', encoding='utf8')
            continue  # Там есть полезная инфа, но книги нет
        except IndexError as e:
            print("Ошибка в поиске")
            print(e.args)
        except etree.XMLSyntaxError:
            print("Ошибка в парсинге")


