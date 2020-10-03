#!/usr/bin/env python
# -*- coding: utf-8 -*-

import book_manager
import metrics
import zipfile

if __name__ == '__main__':
    for book_num in range(1, 200):
        book_path = r'E:\books\flibusta_' + str(book_num) + '.zip'
        try:
            book = book_manager.open_book(book_path)
            print(book)
            break
        except zipfile.BadZipFile:
            # book = open(book_path, 'r', encoding='utf8')
            continue  # Там есть полезная инфа, но книги нет
