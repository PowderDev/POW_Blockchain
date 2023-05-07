import json


def dict_to_bytes(data: dict):
	return json.dumps(data).encode("utf-8")
