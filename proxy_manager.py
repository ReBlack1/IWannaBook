#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import time
from threading import Thread
import asyncio
from proxybroker import Broker


class Proxies:
    _proxy_set = set()  # inside: tuple(str(ip:port), time)
    _buffer_limit = None
    _proxies = asyncio.Queue()
    _broker = Broker(_proxies)
    _tasks = None
    _loop = asyncio.get_event_loop()

    def __init__(self, buffer_limit=20):
        self._buffer_limit = buffer_limit

        print("Инициализация прокси-поисковика завершена")

    def get_new_proxy(self):
        if len(self._proxy_set) > 0:
            min_time_proxy = min(self._proxy_set, key=_return_time_proxy)
            self._proxy_set.discard(min_time_proxy)
            return min_time_proxy[0]

    async def _add(self, proxies):
        while True:
            proxy = await proxies.get()
            if proxy is None: break
            if len(self._proxy_set) < self._buffer_limit:
                await self._proxy_set.add((str(proxy.host) + ":" + str(proxy.port), proxy.avg_resp_time))

    def run_finding(self):
        print("Начинаю поиск прокси")

        self._tasks = asyncio.gather(
            self._broker.find(types=['HTTPS']),
            self._add(self._proxies))
        self._loop.run_until_complete(self._tasks)
        print("После потоков")

    def stop_finding(self):
        print("Завершаю поиск прокси")
        self._loop.stop()


def _return_time_proxy(proxy_tuple):
    return proxy_tuple[1]


async def show(proxies, lst):
    while True:
        proxy = await proxies.get()
        if proxy is None: break
        lst.append(proxy)
    return lst

def get_proxy_set():
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    lst = []

    tasks = asyncio.gather(
        broker.find(types=['HTTPS'], limit=5),
        show(proxies, lst))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)
    return lst