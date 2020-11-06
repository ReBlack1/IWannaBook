import requests as req
import json
from datetime import datetime, timedelta

class BadGateway(Exception):
    pass

def get_proxy(proxy_type):
    data = json.dumps({"method": "get_proxy", "params": {'types': proxy_type}})
    res = req.post("http://127.0.0.1:9090/", data)
    ans = json.loads(res.content.decode())
    # if res.status_code == 500:
    #     raise BadGateway(ans)
    return ans

def unavailable_until(proxy, n=30):
    if not isinstance(proxy, dict):
        raise TypeError('Первым параметром должен быть прокси в виде "HTTP": http://xxx.x.x.x:xxxx')
    data = json.dumps({"method": "unavailable_until", "params": [proxy, n]})
    res = req.post("http://127.0.0.1:9090/", data)
    ans = json.loads(res.content.decode())
    # if res.status_code == 500:
    #     raise BadGateway(ans)
    return ans
