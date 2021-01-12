#!/usr/bin/env python
# coding: utf-8
import json
import requests as req


def get_sintax(text):

    url = "http://lindat.mff.cuni.cz/services/udpipe/api/process?tokenizer&tagger&parser&"
    model = "&model=russian-syntagrus-ud-2.0-170801"
    data = "data=" + text
    final_url = url + data + model

    rep = req.get(final_url)
    return json.loads(rep.content.decode())["result"]

