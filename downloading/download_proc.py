import downloader
import time

for i in range(76, 600):
    print("Скачано = ", i*1000)

    for number in range(1000):
        if number + (1000*i) < 125829:
            continue
        while 1:
            try:
                downloader.flibusta_load_book(number + (1000*i), r'E:\books')
                break
            except Exception as e:
                print("Ошибка на книге", number + (1000*i), str(e))
                time.sleep(2)
