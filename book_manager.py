#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import zipfile
import requests
from lxml import etree
import time
import pickle

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


def flibusta_load_book(number, proxy=None):
    # TODO: check on link
    # TODO: choose path
    """
    Link can:
    1. Has book
    2. Has link
    3. Doesn't load
    4. Doesn't have book
    5. Doesn't have book page (But has page of list of book)

    :param number:  id of book on site
    :param proxy: dict {"https" : "xxx.xxx.xxx.xxx:yyyy"}
    :return: None
    """
    flibusta_url = 'http://flibusta.is/b/' + str(number) + "/fb2"

    req = requests.get(flibusta_url, proxies=proxy)
    path = r"test_books\%s.zip" % str(number)
    f = open(path, "wb")
    f.write(req.content)  # записываем содержимое в файл;
    f.close()


def flibusta_get_book_link(number, proxy=None):
    """

    :param number: id of book on site
    :param proxy: dict {"https" : "xxx.xxx.xxx.xxx:yyyy"}
    :return: id of link
    """
    flibusta_url = 'http://flibusta.is/b/' + str(number)
    req = requests.get(flibusta_url, proxies=proxy)
    html = etree.HTML(req.text)
    XPATH = etree.XPath('//*[@id="main"]/h4/a[2]/@href')
    if len(XPATH(html)) > 0:
        return XPATH(html)[0].split('/')[2]
    return False


def get_status_of_flibusta_book_page(book_number, proxy=None):
    """
    Link can:
    1. Has book
    2. Has link
    3. Doesn't load
    4. Doesn't have book
    5. Doesn't have book page (But has page of list of book)

    :param book_number: id
    :param proxy: dict {"https" : "xxx.xxx.xxx.xxx:yyyy"}
    :return: number of state of book page
    """
    pass

# st = time.time()
# G = BL.compress_book(r"test_books\slugi.zip")
# print("Время обработки = ", str(time.time() - st))
#
# with open(r"graph_models\slugi_graph.plk", 'wb') as f:
#     pickle.dump(G, f)

import asyncio
from proxybroker import Broker




# pr = Proxies()
# print(pr)
# pr.run_finding()
# print(pr.get_new_proxy())
# exit()
# proxy = {"http": "http://" + str(pr[0].host) + ":" + str(pr[0].port)}
# pr.pop(0)

# proxy = {"HTTPS": r"https://SelReBlack1:K1g1GfI@5.44.45.207:45785"}



