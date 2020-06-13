#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
import pickle
from gensim.models import KeyedVectors as KeyVec
import socket
import json
import numpy as np

news_model = r"models\news_2019\model.txt"
tayga_model = r"models\tayga_2019\model.txt"
web_model = r"models\web_2019\web.bin"
model = KeyVec.load_word2vec_format(tayga_model)  # C text format
print("Модель загружена!")


def get_word_by_vec(cur_model, vec):
    ret_word = cur_model.most_similar(positive=[vec], topn=1)
    return ret_word

def get_vector_from_model(cur_model, word):
    try:
        return cur_model.get_vector(word)
    except KeyError:
        return None

temp_vec = None

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(2)  # кол-во подключений
while 1:
    conn, addr = sock.accept()

    print('connected:', addr)

    data = conn.recv(10000)
    print(data)
    print()
    if data.find("get_vector".encode()) != -1:
        req_dict = json.loads(data.decode())
    else:
        req_dict = {"method": "get_word"}
        vec = data
    print("Ользователь попросил: ", req_dict)

    ret_data = b""
    if req_dict.get("method") == "get_vector":
        ans = get_vector_from_model(model, req_dict.get("word"))
        if ans is not None:
            ret_data = ans.tobytes()
    if req_dict.get("method") == "get_word":
        ans = get_word_by_vec(model, np.frombuffer(vec, dtype="float32"))
        if ans is not None:
            ret_data = json.dumps({"res": ans}).encode()

    # print(ret_data)
    # ret_data = json.dumps(ret_data).encode()
    conn.send(ret_data)

    conn.close()