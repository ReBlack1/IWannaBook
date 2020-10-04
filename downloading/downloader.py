#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import zipfile
import requests
from lxml import etree


def flibusta_load_book(number, path, proxy_dict=None):
    # TODO: check on link
    # TODO: choose path
    """
    Link can:
    1. Has book
    2. Has link
    3. Doesn't load
    4. Doesn't have book
    5. Doesn't have book page (But has page of list of book)

    :param number: id of book on site
    :param proxy: dict {"http" : "http://xxx.xxx.xxx.xxx:yyyy"}
    :return: None
    """
    flibusta_url = 'http://flibusta.is/b/' + str(number) + "/fb2"

    headers = {
        'Proxy-Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    req = requests.get(flibusta_url, headers=headers, proxies=proxy_dict)
    path = path + r"\{}.zip".format('flibusta_' + str(number))
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
