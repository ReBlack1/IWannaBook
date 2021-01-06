import PIL
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from text_mining.sintaxis import SintaxisNavec
import re

DIFFERENCE_LENGTHS = 60


def format_text(text, font, x_win, y_win):
    font_size = 50
    font = ImageFont.truetype(font, size=font_size)

    text_list = text.split()
    new_text = []

    print(font.getsize_multiline(text))

    return text, font


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
        vertical_indent = (img.shape[0] - (2 * len(drop_text) - 1) * font_size) / 2  # Рассчитываем отступ по вертикали
    else:  # вертикальное заполнение - центированный текст
        vertical_indent = (img.shape[0] - (len(drop_text) * font_size)) / (
                len(drop_text) + 1)  # Рассчитываем отступ по вертикали
    current_vert_indent = vertical_indent  # текущий вертикальный отступ
    for i in range(len(drop_text)):
        current_w, current_h = font.getsize_multiline(drop_text[i])  # Получаем размеры текущей строки
        current_horiz_indent = (img.shape[1] - current_w) * alignment_horizontal_type[i] + margin[0]
        while current_vert_indent + current_h < (margin[1]):
            current_vert_indent = current_vert_indent + 1
        while current_vert_indent + current_h > (img.shape[0] - margin[3]):
            current_vert_indent = current_vert_indent - 1
        while current_horiz_indent + current_w > (
                img.shape[1] - margin[2]):  # Если с текущим отступом вылезли за края, уменьшим отступ
            current_horiz_indent = current_horiz_indent - 1
        draw.text((current_horiz_indent, current_vert_indent), drop_text[i], fill='rgb(255, 255, 255)', font=font)
        pos = (
            current_horiz_indent, current_vert_indent, current_horiz_indent + current_w,
            current_vert_indent - current_h)
        location.append(pos)
        if alignment_vertical_type == "uniform":  # вертикальное заполнение - равномерно распределенный текст
            current_vert_indent += 2 * font_size  # Выставим новый вертикальный отступ
        else:  # вертикальное заполнение - центированный текст
            current_vert_indent += vertical_indent + font_size
    return location


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
                if zn in splited_text[best_del - 2]:  # Пред. слово было со знаком - ему приоритет
                    return best_del - 1
            return best_del
    return best_del


def split_text(text, sintaxis, count_lines, q_all_nsubj, count_signs):
    splited_text = text.split()
    if count_lines == 1:
        return [text], 1
    if count_lines == 2:
        max_rating = -1
        best_split = None
        for i in range(1, len(splited_text) - 1):
            current_split = [splited_text[:i], splited_text[i:]]
            # for j in range(0, len(current_split)):
            #     txt = ""
            #     for h in current_split[j]:
            #         txt = txt + ' ' + h
            #     current_split[j] = txt
            current_rating = splitting_rating(current_split, sintaxis, q_all_nsubj, count_signs)
            print(current_rating)
            if current_rating >= max_rating:
                max_rating = current_rating
                best_split = current_split
        for j in range(0, len(best_split)):
            txt = ""
            for h in best_split[j]:
                txt = txt + ' ' + h
            best_split[j] = txt
        best_split[0] = best_split[0][1:]
        return best_split, max_rating


def splitting_rating(split, sintaxis, q_all_nsubj, count_signs):
    count_signs_at_end = 0
    for i in range(0, len(split) - 1):
        # if split[i][-1] in "{}.,-<>\";:\!?[\]\\\/":
        if split[i][-1][-1] in "{}.,-<>\";:\!?[\]\\\/":
            count_signs_at_end = count_signs_at_end + 1
        q_inside_nsubj = 0
        for j in q_all_nsubj:
            if (j[0] >= len(split[0]) - 1 and j[1] >= len(split[0]) - 1) or (
                    j[0] < len(split[0]) - 1 and j[1] < len(split[0]) - 1):
                q_inside_nsubj = q_inside_nsubj + 1
        q_inside_nsubj = len(q_all_nsubj) - q_inside_nsubj
    return (q_inside_nsubj + count_signs_at_end) / (len(q_all_nsubj) + count_signs)


def put_text_pil(params):
    sint_maker = SintaxisNavec()
    text = params["text"]
    count_lines = params["count_lines"]
    sintaxis = sint_maker.get_sintaxis(text)
    count_signs = len(re.findall("[{}.,-<>\";:!?[\]\\\/]", text))
    q_all_nsubj = []
    for i in sintaxis[1]:
        if i[2] == "nsubj":
            q_all_nsubj.append(i)
    splitted_text = split_text(text, sintaxis, count_lines, q_all_nsubj, count_signs)
    img = np.zeros((256, 512, 3), np.uint8)  # или cv2.imread("path_to_file")
    img[:, :, :] = 0
    im = Image.fromarray(img)
    drop_text = splitted_text[0]
    test_text = "\n".join(drop_text)
    print("Разбивка:\n" + test_text)
    font_size = find_font_size(test_text, '19925.ttf', im.width - 40, im.height)
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
        if (len(i) < cur_min):
            cur_min = len(i)
        if (len(i) > cur_max):
            cur_max = len(i)
    dif = cur_min * 100.0 / cur_max
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
    # print(split_text(i))
    pass

img = np.zeros((256, 512, 3), np.uint8)  # или cv2.imread("path_to_file")
img[:, :, :] = 0
params = {"text": "Будь осторожен. Одна ошибка - и ты ошибся.", "count_lines": 2}
img = put_text_pil(params)
cv2.imshow('Result', img)
cv2.waitKey()
