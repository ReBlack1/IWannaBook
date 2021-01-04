import PIL
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import time

DIFFERENCE_LENGTHS = 60

def format_text(text, font, x_win, y_win):
    font_size = 50
    font = ImageFont.truetype(font, size=font_size)

    text_list = text.split()
    new_text = []


    print(font.getsize_multiline(text))

    return text, font

def get_best_del(splited_text, part, size):
    best_del = 1
    for i in range(1, len(splited_text) - 1):
        first_part = " ".join(splited_text[:i])
        if len(first_part) < size * part:
            best_del = i
        else:
            for zn in [",", "-", "."]:  # Учтем знаки препинания
                if zn in splited_text[best_del]:  # След. слово со знаком - ему приоритет
                    return best_del + 1
                if zn in splited_text[best_del-2]:  # Пред. слово было со знаком - ему приоритет
                    return best_del - 1
            return best_del
    return best_del

def split_text(text):
    size_list = [
        None,
        [1],
        [2/3, 2/3],
        [3/4, 2/3, 1/4],
        [3/4, 3/4, 3/4, 1/2]
    ]
    splited_text = text.split()
    if len(text) <= 15:
        return [text]

    if len(text) <= 45:
        k = sum(size_list[2])
        best_del = get_best_del(splited_text, size_list[2][0] / k, len(text))
        return [" ".join(splited_text[:best_del]),
                " ".join(splited_text[best_del:])]

    if len(text) <= 95:
        k = sum(size_list[3])
        best_del1 = get_best_del(splited_text, size_list[3][0] / k, len(text))
        best_del2 = get_best_del(splited_text[best_del1:], size_list[3][1] / k, len(text)) + best_del1
        return [" ".join(splited_text[:best_del1]),
                " ".join(splited_text[best_del1:best_del2]),
                " ".join(splited_text[best_del2:])]

    if len(text) <= 180:
        k = sum(size_list[4])
        best_del1 = get_best_del(splited_text, size_list[4][0] / k, len(text))
        best_del2 = get_best_del(splited_text[best_del1:], size_list[4][1] / k, len(text)) + best_del1
        best_del3 = get_best_del(splited_text[best_del2:], size_list[4][2] / k, len(text)) + best_del2

        return [" ".join(splited_text[:best_del1]),
                " ".join(splited_text[best_del1:best_del2]),
                " ".join(splited_text[best_del2:best_del3]),
                " ".join(splited_text[best_del3:])]

def find_font_size(test_text, font_path, x_win, y_win):
    best_size = 10
    for i in range(10, 100):
        font = ImageFont.truetype(font_path, size=i)
        text_size = font.getsize_multiline(test_text)
        if text_size[0] < x_win:
            best_size = i
        else:
            return best_size

def add_text_to_photo(draw, alignment_vertical_type, alignment_horizontal_type, margin, drop_text, font_size, font):
    """
    :param draw: обьект, на котором рисуем
    :param alignment_vertical_type: тип вертикального выравнивания
    :param alignment_horizontal_type: коэффицент горизонтального отступа для каждой строки(число от 0 до 1)
    :param margin: отступы от края картинки(лево, верх, право, низ)
    :param drop_text: разбитый на строки текст
    :param font_size: размер шрифта
    :param font: шрифт
    :return:
    """
    location = []
    if alignment_vertical_type == "uniform":  # вертикальное заполнение - равномерно распределенный текст
        vertical_indent = (img.shape[0] - (2 * len(drop_text) - 1)*font_size) / 2  # Рассчитываем отступ по вертикали
    else:  # вертикальное заполнение - центированный текст
        vertical_indent = (img.shape[0] - (len(drop_text)*font_size))/(len(drop_text)+1)  # Рассчитываем отступ по вертикали
    current_vert_indent = vertical_indent  # текущий вертикальный отступ
    for i in range(len(drop_text)):
        current_w, current_h = font.getsize_multiline(drop_text[i])  # Получаем размеры текущей строки
        current_horiz_indent = (img.shape[1] - current_w) * alignment_horizontal_type[i] + margin[0]
        while current_vert_indent + current_h < (margin[1]):
            current_vert_indent = current_vert_indent + 1
        while current_vert_indent + current_h > (img.shape[0] - margin[3]):
            current_vert_indent = current_vert_indent - 1
        while current_horiz_indent + current_w > (img.shape[1] - margin[2]):  # Если с текущим отступом вылезли за края, уменьшим отступ
            current_horiz_indent = current_horiz_indent - 1
        draw.text((current_horiz_indent, current_vert_indent), drop_text[i], fill='rgb(255, 255, 255)', font=font)
        pos = (current_horiz_indent, current_vert_indent, current_horiz_indent+current_w, current_vert_indent-current_h)
        location.append(pos)
        if alignment_vertical_type == "uniform":  # вертикальное заполнение - равномерно распределенный текст
            current_vert_indent += 2*font_size  # Выставим новый вертикальный отступ
        else:  # вертикальное заполнение - центированный текст
            current_vert_indent += vertical_indent + font_size
    return location

def put_text_pil(img: np.array, txt):
    im = Image.fromarray(img)
    drop_text = split_text(txt)
    test_text = "\n".join(drop_text)
    print("Разбивка:\n" + test_text)
    font_size = find_font_size(test_text, '19925.ttf', im.width-40, im.height)
    font = ImageFont.truetype('19925.ttf', size=font_size)
    # здесь узнаем размеры сгенерированного блока текста
    w, h = font.getsize_multiline(test_text)
    print(w, h)
    #im = Image.fromarray(img)
    im = Image.open("fon.jpg")
    draw = ImageDraw.Draw(im)
    # Подсчет процентного соотношения самой длинной и самой короткой строк
    cur_min = 200
    cur_max = 0
    for i in drop_text:
        if(len(i) < cur_min):
            cur_min = len(i)
        if(len(i) > cur_max):
            cur_max = len(i)
    dif = cur_min*100.0/cur_max
    print(dif)
    # Вывод текста с различными отступами
    add_text_to_photo(draw, "uniform", (0, 0.5, 1, 0), (20, 20, 20, 20), drop_text, font_size, font)
    im.save("test_img.png", "png")

    img = np.asarray(im)

    return img

wolf_idea = [
    "Кем бы ты ни был, кем бы ты не стал, помни, где ты был и кем ты стал.",
    "Легкой бывает только легкая дорога. Тяжелая дорога всегда трудна.",
    "Лучше один раз упасть, чем сто раз упасть.",
    "Легко вставать, когда ты не ложился.",
    "Сделал дело — дело сделано.",
    "За двумя зайцами погонишься — рыбку из пруда не выловишь, делу время, а отмеришь семь раз.",
    "Даже если нет шансов, всегда есть шанс.",
    "Громко — это как тихо, только громче.",
    "Будь осторожен. Одна ошибка - и ты ошибся.",
    "Привет, мир!"
]
for i in wolf_idea:
    print(split_text(i))

img = np.zeros((256, 512, 3), np.uint8)  # или cv2.imread("path_to_file")
img[:, :, :] = 0
img = put_text_pil(img, "Кем бы ты ни был, кем бы ты не стал, помни, где ты был и кем ты стал.")
cv2.imshow('Result', img)
cv2.waitKey()
