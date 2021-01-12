#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import json
import numpy as np
import re
import requests

def preprocess_text(text):
    """
    Предпроцессинг текста:
    Замена url, замена ё на е, приведение в нижний регистр,
    Удаление знаков препинания,
    :param text:
    :return:
    """
    if text is None:
        return ""
    text = text.lower().replace("ё", "е")
    text = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+))', 'URL', text)
    text = re.sub(r'[^a-zA-Zа-яА-Я1-9]+', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


def get_vec(token_word):
    data = json.dumps({"method": "get_vec", "params": [token_word]})
    res = requests.post("http://127.0.0.1:9095/", data)
    if not res:
        return None
    vec = np.frombuffer(res.content, dtype="float32")
    return vec

def get_str_vec(word, serv_host='localhost', serv_port=9090, resp_len=2048):
    sock = socket.socket()
    sock.connect((serv_host, serv_port))
    req_dict = {"method": "get_vector", "word": word}
    sock.send(json.dumps(req_dict).encode())
    data = sock.recv(resp_len)
    sock.close()
    return data


def get_word_by_vec(bytes_vec, serv_host='localhost', serv_port=9090, resp_len=2048):
    if len(bytes_vec) != 1200:
        return json.dumps({"res": [("ERROR_NOUN", 0)]}).encode()
    sock = socket.socket()
    sock.connect((serv_host, serv_port))
    req_dict = {"method": "get_word"}
    sock.send(bytes_vec)
    data = sock.recv(resp_len)
    sock.close()
    return data


def correct_token(token):
    if token in ["ADJS", "ADJF", "COMP"]:
        return "ADJ"
    if token in ["NPRO"]:
        return "NOUN"
    if token in ["PRCL", "ADVB", "CONJ"]:
        return "ADV"
    if token in ["PREP"]:
        return "PROPN"
    if token in ["INFN"]:
        return "VERB"
    return token




# morph = pymorphy2.MorphAnalyzer()
#
# psy_sec = "Вопрос о деньгах действует также просто как рубль. Глупость является преимуществом богатых. Это всегда раздражает бедных. Манифест — это импульс ожидания своего перевоплощения. Террористы заслуживают приветствия. Для успеха этого манифеста необходим только террор."
# psy_sec = 'думаю над твоим "обиделся" Ты это сделал совершенно не их переживай и чувства обиды. Просто хотел внимания. Я все это время переживаю и чувствую себя плохой. Хотя совершенно не знаю, как я могу повлиять на ситуацию и что я должна сделать и должна ли вообще, чтобы общаться больше и интереснее. Это ты не отвечает на большинство моих сообщений и не интересуешься какой бытовухлц я занимаюсь, мне же интересно все, что ты рассказываешь. Может у тебя жизнь интересней? Не бросай просить так обид, если нет на них причин.'
# psy_sec = "террорист интересно"
# psy_list = preprocess_text(psy_sec).split()
# vec_list = []
# for word in psy_list:
#     if len(word) == 1:
#         continue
#     norm_word = morph.parse(word)[0]
#     token_word = norm_word.normal_form + "_" + correct_token(norm_word.tag.POS)
#     print(token_word)
#     result = get_vec(token_word)
#     vec_list.append(result)
#
# sim_matrix = create_sim_map(vec_list)
# for line in sim_matrix:
#     print(line)

