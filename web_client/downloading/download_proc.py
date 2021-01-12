import downloading.downloader as downloader
import time

for number in range(400000, 500000):
    if number % 1000 == 0:
        print("Скачано " + str(number))
    while 1:
        try:
            downloader.flibusta_load_book(number, r'E:\books')
            break
        except Exception as e:
            print("Ошибка на книге", number, str(e))
            time.sleep(2)
