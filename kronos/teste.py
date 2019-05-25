import json

with open('kytos.json', 'r') as kytos_json:
	obj = json.loads(kytos_json.read())['version']
	kytos_json.close()
print(obj)