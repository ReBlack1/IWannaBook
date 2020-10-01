import re
import time
from collections import Counter
import math
import requests
from lxml import html

def transliterate(name):
    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '-', '~': '', '.': '', '!': '', '@': '', '#': '',
              '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '-', '=': '', '+': '',
              ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
              '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
              'Є': 'e', '—': ''}
    for key in slovar:
        name = name.replace(key, slovar[key])
    return name

#заменить на другой вариант. Формируем поисковую строку. Ищем точное соответствие. Если его не найдено, то выкинуть ошибку
def get_html(author, book_name):
    author = transliterate(author).lower()
    book_name = transliterate(book_name).lower()
    url = f'https://www.litres.ru/{author}/{book_name}/'
    r = requests.get(url)
    print(f'url: {url}')
    #r = requests.get(f'https://www.litres.ru/evgeniy-zamyatin/my-russkaya-antiutopiya/').text
    return r

def get_rating(author, book_name):
    try:
        ht = get_html(author, book_name)
        ht = html.fromstring(ht.content)
        rating = ht.xpath('//div[@class="rating-number bottomline-rating"]/text()')[0]
        count = ht.xpath('//div[@class="votes-count bottomline-rating-count"]/text()')[0]
        #g = ht.xpath('//div[@class="biblio_book_info"]/ul/li/a')
        #найти ребенка span и дописать из него первую букву
        #print(dir(g))
    except IndexError as e:
        print(f'Информация о книге не найдена, {e}')
        rating = count = None
    slovar = {'reting': rating, 'count': count}
    return slovar

def compute_tf(text):
    tf_text = Counter(text)
    for i in tf_text:
        tf_text[i] = tf_text[i] / float(len(text))
    return tf_text

def compute_idf(word, corpus):
    return math.log10(len(corpus) / sum([1.0 for i in corpus if word in i]))

def compute_tfidf(count_books):
    """
    Определяет TF-IDF
    """
    for i in range(0,count_books):
        # открыть файл с текстом.
        tf_dict = compute_tf('')#пихнуть сюда
        #если tf содержался, то увеличить на 1 счетчик(словарь знаменателя). если не содержался, то добавить новую пару
        #сохранить результаты в другой папке через pickle

    #создать словарь с посчитанными idf. сохранить его
    documents_list = []
    for text in corpus:
        tf_idf_dictionary = {}
        computed_tf = compute_tf(text)
        for word in computed_tf:
            tf_idf_dictionary[word] = computed_tf[word] * compute_idf(word, corpus)
        documents_list.append(tf_idf_dictionary)
    return documents_list

def is_mat(word):
    """
    Определяет является слово бранным или нет
    """
    _mats = {r'(ху(й|е|ё|и|я|ли[^а-я])\w*)',
             r'(п(и|е|ё)(з|с)д)\w*',
             r'([^а-я])(би?ля(д|т|[^а-я]))\w*',
             r'(пид(о|а)р|п(е|и)дри)\w*',
             r'(муд(ак|ач|о|и))\w*',
             r'(([^а-я]|по|на|от|не|ни)(х|x)(е|e)(р|p))\w*',
             r'(з(а|о)луп(а|и))\w*',
             r'(([^а-я]у?|под?|на|за|от|вы|ь|ъ)(е|ё|и)б(а|ыр|у|нут|ись|ище))\w*',
             r'([^а-я])((на|по)х)([^а-я])\w*',
             r'(су(ка|чк|ки|чь))\w*',
             r'(др(оч|ачи))\w*',
             r'((\W|о|за)трах)\w*'}
    for reg in _mats:
        if re.search(reg, word) is not None:
            return True
    return False

def count_mats(text):
    """
    Считает количество бранных слов в тексте
    """
    text = text.lower()
    word = re.split('!?;-| |, |\n', text)
    count = 0
    for slovo in word:
        if is_mat(slovo):
            count+=1
            #print(slovo)
    return count

text = 'превысокомногорассмотрительствующий ' * 30000
#while True:
#    x = input()
#    if x:
#        text += x + '\n'
#    else:
#        break
start = time.time()
print(count_mats(text))
end = time.time()
print(f'{end-start} секунд')


#corpus = [['pasta', 'la', 'vista', 'baby', 'la', 'vista'],
#['hasta', 'siempre', 'comandante', 'baby', 'la', 'siempre'],
#['siempre', 'comandante', 'baby', 'la', 'siempre']]
#print(compute_tfidf(corpus))


