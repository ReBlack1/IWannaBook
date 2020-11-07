from metrics import LitresParser, create_new_proxy, BookNotFound, CaptchaException
import requests
import config
from base_analys.base_helper import get_base_info_from_book_xml
import book_manager
import zipfile
import lxml
import pickle

proxies = create_new_proxy()
litres = LitresParser(proxies)

if __name__ == '__main__':
    for book_num in range(13753, 170000):
        book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'
        rating_path = config.raiting_path + r"\raiting_flibusta_" + str(book_num) + '.plc'
        while True:
            try:
                # print(litres.get_rating('Фридрих Шиллер', 'Разбойники'))
                book_xml = book_manager.open_book(book_path)
                book_info = get_base_info_from_book_xml(book_xml)
                author = book_info["author_name"] + " " + book_info["author_second_name"]
                book_name = book_info["title"]
                print(book_num, book_info)
                raiting = litres.get_rating(author, book_name)
                print(raiting)
                with open(rating_path, 'wb') as f:
                    clf = pickle.dump(raiting, f)
                    print("Сохранено :) ")
                break
            except BookNotFound as e:
                print(e)
                break
            except CaptchaException:
                print('Капча.', 'Меняем прокси на новый')
                proxies = create_new_proxy()
                litres.set_proxy(proxies)
            except requests.exceptions.ConnectionError:
                print('Не получили доступ к сайту.', 'Меняем прокси на новый')
                proxies = create_new_proxy()
                litres.set_proxy(proxies)
            except requests.exceptions.ReadTimeout:
                print('Упали по таймауту.', 'Меняем прокси на новый')
                proxies = create_new_proxy()
                litres.set_proxy(proxies)
            except zipfile.BadZipFile:
                # print("Файл не является зип-архивом")
                break
            except lxml.etree.XMLSyntaxError:
                break
            except FileNotFoundError:
                break