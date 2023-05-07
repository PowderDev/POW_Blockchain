import hashlib
import json


def crypto_hash(*args) -> str:
	stringified_args = map(lambda arg: json.dumps(arg), args)
	joined_args = "".join(stringified_args)
	encoded_args = joined_args.encode("utf-8")
	
	return hashlib.sha256(encoded_args).hexdigest()
