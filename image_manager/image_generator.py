import PIL
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from IWannaBook.text_mining.sintaxis import SintaxisNavec
import re
from guppy import hpy
import time

DIFFERENCE_LENGTHS = 60
W = 512
H = 256
STANDARD_FONT_SIZE = 16


def find_font_size(test_text, font_path, x_win, y_win):
    best_size = 10
    for i in range(10, 100):
        font = ImageFont.truetype(font_path, size=i)
        text_size = font.getsize_multiline(test_text)
        if text_size[0] < x_win:
            best_size = i
        else:
            return best_size


def find_count_signs(text):
    return len(re.findall("[{}.,-<>\";:!?[\]\\\/]", text))


def get_nsubj_list(sintaxis):
    q_all_nsubj = []
    for syntactic_links in sintaxis[1]:
        if syntactic_links[2] == "nsubj":
            q_all_nsubj.append(syntactic_links)
    return q_all_nsubj


def find_dif(cur_text):
    cur_min = 200
    cur_max = 0
    for syntactic_links in cur_text:
        if (len(syntactic_links) < cur_min):
            cur_min = len(syntactic_links)
        if (len(syntactic_links) > cur_max):
            cur_max = len(syntactic_links)
    dif = cur_min / cur_max * 100
    return dif


def find_alignment_vertical_type(dif, count_lines):
    if count_lines > 2 and dif < DIFFERENCE_LENGTHS:
        return "uniform"
    return "centre"


def add_text_to_photo(img, draw, alignment_vertical_type, alignment_horizontal_type, margin, drop_text, font_size, font):
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
    try:
        w, h = font.getsize_multiline(drop_text[0])
    except IndexError:
        return None
    if alignment_vertical_type == "uniform":  # вертикальное заполнение - равномерно распределенный текст
        vertical_indent = (img.shape[0] - h * len(drop_text) - margin[1] - margin[3]) / len(
            drop_text) + 1  # Рассчитываем отступ по вертикали
    else:  # вертикальное заполнение - центированный текст
        vertical_indent = (img.shape[0] - h * (2 * len(drop_text) - 1) - margin[1] - margin[
            3]) / 2  # Рассчитываем отступ по вертикали
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
            current_vert_indent += vertical_indent  # Выставим новый вертикальный отступ
        else:  # вертикальное заполнение - центированный текст
            current_vert_indent += 2 * h
    return location


def remove_all(text, sep):
    try:
        while True:
            text.remove(sep)
    except ValueError:
        pass


def split_text(text, count_lines, q_all_nsubj, count_signs):
    splited_text = re.split("(\W)", text)
    remove_all(splited_text, '')
    remove_all(splited_text, ' ')
    splited = {}
    if count_lines == 1:
        return {1: [[splited_text]]}
    if count_lines == 2:
        for i in range(1, len(splited_text) - 1):
            current_split = [splited_text[:i], splited_text[i:]]
            current_rating = splitting_rating(current_split, q_all_nsubj, count_signs)
            try:
                splited[current_rating].append(current_split)
            except BaseException:
                splited[current_rating] = []
                splited[current_rating].append(current_split)
        return splited
    if count_lines == 3:
        for i in range(1, len(splited_text) - 1):
            for j in range(i + 1, len(splited_text)):
                current_split = [splited_text[:i], splited_text[i:j], splited_text[j:]]
                current_rating = splitting_rating(current_split, q_all_nsubj, count_signs)
                try:
                    splited[current_rating].append(current_split)
                except BaseException:
                    splited[current_rating] = [current_split]
        return splited
    if count_lines == 4:
        for i in range(1, len(splited_text) - 2):
            for j in range(i + 1, len(splited_text)):
                for k in range(j + 1, len(splited_text)):
                    current_split = [splited_text[:i], splited_text[i:j], splited_text[j:k], splited_text[k:]]
                    print(current_split)
                    current_rating = splitting_rating(current_split, q_all_nsubj, count_signs)
                    try:
                        splited[current_rating].append(current_split)
                    except BaseException:
                        splited[current_rating] = [current_split]
        return splited


def splitting_rating(split, q_all_nsubj, count_signs):
    count_signs_at_end = 0
    for i in range(0, len(split)):
        if split[i][-1][-1] in "{}.,-<>\";:\!?[\]\\\/":
            count_signs_at_end = count_signs_at_end + 1
    q_inside_nsubj = 0
    len_split_1 = len(split[0])
    len_split_2 = len(split[1]) + len_split_1
    for j in q_all_nsubj:
        if (j[0] < len_split_1 and j[1] < len_split_1) or (
                j[0] >= len_split_1 and j[0] < len_split_2 and j[1] >= len_split_1 and j[1] < len_split_2) or (
                j[0] >= len_split_2 and j[1] >= len_split_2):
            q_inside_nsubj = q_inside_nsubj + 1
    try:
        rating = (q_inside_nsubj + count_signs_at_end) / (len(q_all_nsubj) + count_signs)
    except ZeroDivisionError:
        rating = 0
    return rating


def exclude_bad_phrases(splitted_text):
    delete_list = []
    for text in splitted_text:
        # for j in range(0, len(text)):
        for j in range(0, len(text) - 1):
            if len(text[j]) < len(text[j + 1]) or len(text[j]) == 1 or len(text[j + 1]) == 1:
                #    if len(text[j]) == 1:
                delete_list.append(text)
                break
    if len(delete_list) == len(splitted_text):
        return None
    for i in delete_list:
        splitted_text.remove(i)
    return splitted_text


def merge_str(drop_text):
    for phrase in drop_text:
        for j in range(0, len(phrase)):
            tmp = ""
            for i in range(0, len(phrase[j])):
                if phrase[j][i] in "{}.,-<>\";:\!?[\]\\\/":
                    tmp = tmp + phrase[j][i]
                else:
                    tmp = tmp + ' ' + phrase[j][i]
            tmp = tmp[1:]
            phrase[j] = tmp
    return drop_text


def position_rating(img, draw, alignment_vertical_type, alignment_horizontal_type, margin, drop_text, font_size, font):
    location = add_text_to_photo(img, draw, alignment_vertical_type, alignment_horizontal_type, margin, drop_text, font_size,
                                 font)
    for i in location:
        if i[0] < margin[0] or i[0] > W - margin[2] or i[1] < margin[1] or i[1] > H - margin[3] or i[2] > W - margin[
            2] or i[2] < margin[0] or i[3] < margin[1] or i[3] > H - margin[3]:
            return None, None
    window_w = img.shape[1] - margin[0] - margin[2]
    summ = 0.0
    max_w = -1
    max_h = -1
    for i in range(0, len(drop_text)):
        cur_w = location[i][2] - location[i][0]
        cur_h = location[i][1] - location[i][3]
        if cur_w > max_w:
            max_w = cur_w
        if cur_h > max_h:
            max_h = cur_h
        real_w = cur_w / window_w
        good_w = 1.0 * alignment_horizontal_type[i] * window_w
        summ = summ + (1.0 / abs(good_w - real_w))
        qsh = max_h / max_w
    return summ, qsh


def put_text_pil(params):
    sint_maker = SintaxisNavec()
    text = params["text"]
    font = params["font"]
    count_lines = params["count_lines"]
    img_path = params["img_path"]
    margin = params["margin"]
    alignment_horizontal_type = params["alignment_horizontal_type"]

    sintaxis = sint_maker.get_sintaxis(text)
    count_signs = find_count_signs(text)
    q_all_nsubj = get_nsubj_list(sintaxis)
    splitted_text = split_text(text, count_lines, q_all_nsubj, count_signs)

    list_keys = list(splitted_text.keys())
    list_keys.sort(reverse=True)
    for cur_rating in list_keys:
        drop_text = exclude_bad_phrases(splitted_text[cur_rating])
        if drop_text is None:
            continue
        spl_rating = cur_rating
        break
    spl_rating = spl_rating * count_lines
    drop_text = merge_str(drop_text)  # Лучшие разбивки по смыслу
    print("Лучшие разбиения(по смыслу):")
    print(drop_text)

    best_pos_rating = -1
    best_split = ""
    img = np.zeros((H, W, 3), np.uint8)
    img[:, :, :] = 0
    im = Image.fromarray(img)
    draw = ImageDraw.Draw(im)
    for cur_text in drop_text:
        test_text = "\n".join(cur_text)
        font = params["font"]
        font_size = find_font_size(test_text, font, im.width - margin[0] - margin[2],
                                   im.height - margin[1] - margin[3])
        font = ImageFont.truetype(font, size=font_size)
        # Подсчет процентного соотношения самой длинной и самой короткой строк
        dif = find_dif(cur_text)
        # Выбор типа вертикального выравнивания
        alignment_vertical_type = find_alignment_vertical_type(dif, count_lines)
        pos_rating, qsh = position_rating(img, draw, alignment_vertical_type, alignment_horizontal_type, margin,
                                          cur_text,
                                          font_size, font)
        if pos_rating is None or qsh is None:
            print("Текст не помещается на картинку!")
            continue

        pos_rating = pos_rating * count_lines
        if pos_rating > best_pos_rating:
            best_pos_rating = pos_rating
            best_split = cur_text

    if not isinstance(best_split, list) and len(best_split) < 2:
        return None, 10000000000

    print("-----------------------")
    print("Лучшее разбиение: ", best_split)
    print("Рейтинг разбиения:", str(spl_rating))
    print("Рейтинг позиционирования:", str(best_pos_rating))
    print("Отношение максимальной высоты к максимальной длине:", str(qsh))
    print("-----------------------\n\n")

    if img_path is None:
        img = np.zeros((H, W, 3), np.uint8)
        img[:, :, :] = 0
        im = Image.fromarray(img)
    else:
        im = Image.open(img_path)
    draw = ImageDraw.Draw(im)
    add_text_to_photo(img, draw, alignment_vertical_type, alignment_horizontal_type, margin, best_split, font_size, font)
    im.save(f"final_img{count_lines}.png", "png")  # Сохраняет лучшую картинку

    # img = np.asarray(im)
    return im, font_size


def find_best_photo(img_list, font_size_list):
    dif = 200
    for i in range(0, len(img_list)):
        if abs(font_size_list[i] - STANDARD_FONT_SIZE) < dif:
            best_img = img_list[i]
            dif = abs(font_size_list[i] - STANDARD_FONT_SIZE)
    return best_img


def text_on_picture(text, img_path=None, font="14539.ttf", margin=(20, 20, 20, 20),
                    alignment_horizontal_type=(1, 1, 1, 1)):
    img_list = []
    font_size_list = []
    # img = np.zeros((H, W, 3), np.uint8)
    # img_path = "fon.jpg"
    params = {"text": text, "font": font, "img_path": img_path,
              "margin": margin, "alignment_horizontal_type": alignment_horizontal_type}
    for count_line in range(1, 5):
        print("Длина разбиения: ", str(count_line))
        params['count_lines'] = count_line
        cur_img, font_size = put_text_pil(params)
        img_list.append(cur_img)
        font_size_list.append(font_size)
    best_img = find_best_photo(img_list, font_size_list)
    #best_img.save("BEST.png", "png")  # Сохраняет лучшую картинку
    return best_img

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

if __name__ == '__main__':
    # start = time.time()
    text = "Даже если нет шансов, всегда есть шанс."
    best_img = text_on_picture(text)
    best_img.save("BEST.png", "png")
    # best_img = np.asarray(best_img)
    # cv2.imshow('Result', best_img)
    # h = hpy()
    # end = time.time()
    # print(end - start)
    # print(h.heap())
    # cv2.waitKey()
