#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import zipfile
import requests
from lxml import etree


def open_fb2_book(path, code='UTF-8'):
    """
    Book format is fb2
    :param path: path of book
    :param code:
    :return: text of book in xml format
    """
    handle = open(path, 'rb')
    data = handle.read().decode(encoding=code)
    return data


def open_bytes_book_in_zip(path):
    """
    book format fb2 inside zip-archive
    :param path: path of archive
    :return: text of book in xml-format
    """
    if zipfile.is_zipfile(path):
        zf = zipfile.ZipFile(path)
        for zip_filename in zf.namelist():
            data = zf.read(zip_filename)
            if data.startswith(b'<?xml'):
                break
        else:
            raise FileNotFoundError("Внутри архива нет xml")
    else:
        raise zipfile.BadZipFile("File has different compression format")
    return data


def open_book(path):
    return open_bytes_book_in_zip(path)
