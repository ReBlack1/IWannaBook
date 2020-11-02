import requests as req
import json

def get_proxy(proxy_type):
    types = {'types': proxy_type}
    res = req.get(url="http://127.0.0.1:9090", params=types)
    return json.loads(res.content.decode())
