import BL
import pickle
import time
import cProfile
import networkx as nx
import matplotlib.pyplot as plt
import asyncio
from book_manager import flibusta_load_book, open_book
import requests
from proxybroker import Broker
import zipfile


def compressing():
    for num in range(32800, 40000):
        path = r"test_books\%s.zip" % str(num)
        try:
            book = open_book(path)  # Проверка нормальный ли файл
            plc_path = r'graph_models\{}_graph.plc'.format(str(num))
            book_dict = BL.compress_book(path)
            print(num, book_dict)
            with open(plc_path, 'wb') as f:
                pickle.dump(book_dict, f)
        except zipfile.BadZipFile:
            continue

# compressing()

# st = time.time()
# G = cProfile.run(r'BL.compress_book(r"test_books\1.zip")')
# G = BL.compress_book(r"test_books\3.zip")

# print("Время обработки = ", str(time.time() - st))
# with open(r"graph_models\3_graph.plk", 'wb') as f:
#     pickle.dump(G, f)


# with open(r"graph_models\5144_graph.plc", 'rb') as f:
#     G = pickle.load(f)["graph"]
# node_color = [(G.degree(v))*3 for v in G]
# node_size = [400 * nx.get_node_attributes(G, 'size')[v] for v in G]
# nx.draw(G, nlist=[G.nodes], with_labels=True, node_color=node_color, font_color="k", node_size=node_size)
# plt.show()

# G = None
# with open(r"graph_models\3_graph.plk", 'rb') as f:
#     G = pickle.load(f)
# st = time.time()
# BL.make_scene(G)
# print("Время обработки = ", str(time.time() - st))


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
        broker.find(types=['HTTP'], limit=20),
        show(proxies, lst))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)
    return lst


def download():
    proxy_set = get_proxy_set()
    pr = proxy_set.pop(0)
    proxy = {"http": "http://" + str(pr.host) + ":" + str(pr.port)}
    print(proxy)

    for i in range(39000, 40000):
        while True:
            try:
                # span style="size"
                flibusta_url = 'http://flibusta.is/b/' + str(i)
                req = requests.get(flibusta_url, proxies=proxy)
                cont = req.content.decode()
                # print(len(cont))
                if len(cont) in [816, 4796]:  # Прокси не подходит
                    raise Exception
                pages = None
                for line in cont.split("\n"):
                    if line.find('<span style=size>') != -1:
                        pages = line.split('<span style=size>')[1].split("</span>")[0]
                        # print(pages)
                        try:
                            pages = int(pages.split()[1])
                        except:
                            pages = None
                            break
                        break
                if pages is None or pages > 70 or pages < 30:
                    break
                print(i)
                flibusta_load_book(i, proxy=proxy)
                break
            except Exception as e:
                print(e)
                print(e.args)
                time.sleep(5)
                if len(proxy_set) == 0:
                    while 1:
                        try:
                            proxy_set = get_proxy_set()
                            break
                        except Exception as e:
                            print(e)
                            print(e.args)
                            continue
                pr = proxy_set.pop(0)
                proxy = {"http": "http://" + str(pr.host) + ":" + str(pr.port)}

# download()


with open("catalog.plc", 'rb') as f:
    catalog = pickle.load(f)

def make_catalog():
    with open("catalog.plc", 'rb') as f:
        catalog = pickle.load(f)
    print(len(catalog))

    for num in range(10000, 40000):
        plc_path = r'graph_models\{}_graph.plc'.format(str(num))
        try:
            if num in catalog.keys():
                continue
            with open(plc_path, 'rb') as f:
                book = pickle.load(f)
            print()

            print(num, book)
            info = BL.make_scene(book["graph"])
            catalog[num] = (book["book_title"], book["author"], info)
        except FileNotFoundError:
            continue

    with open("catalog.plc", 'wb') as f:
        book = pickle.dump(catalog, f)
