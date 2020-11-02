import requests as req
import json
from datetime import datetime, timedelta

def get_proxy(proxy_type):
    types = {'types': proxy_type}
    res = req.get(url="http://127.0.0.1:9090", params=types)
    return json.loads(res.content.decode())

def unavailable_until(proxy, n=30):
    proxy['unavailable_until'] = datetime.now() + timedelta(seconds=n)
