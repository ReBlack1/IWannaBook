import json
temp_dict = {"function": "get_proxy", 'params': [["HTTPS"]]}
json_req = json.dumps(temp_dict)
print("Успешно отработал", json_req)
