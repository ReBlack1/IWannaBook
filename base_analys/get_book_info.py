import config
from base_analys.base_helper import get_base_info_from_book_xml
import book_manager
import zipfile
import lxml
import pickle

if __name__ == '__main__':
    book_info_list = []
    for book_num in range(0, 150000):
        book_path = config.raw_book_path + r'\flibusta_' + str(book_num) + '.zip'
        try:
            if book_num % 1000 == 0:
                print(book_num)
            book_xml = book_manager.open_book(book_path)
            book_info = get_base_info_from_book_xml(book_xml)
            book_info["book_num"] = book_num


            book_info_list.append(book_info)
        except zipfile.BadZipFile:
            pass
        except lxml.etree.XMLSyntaxError:
            pass
        except FileNotFoundError:
            pass

    with open(r'E:\books_info_list.plc', 'wb') as f:
        clf = pickle.dump(book_info_list, f)
        print("Сохранено :) ")