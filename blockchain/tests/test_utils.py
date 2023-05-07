from blockchain.utils.hash import crypto_hash
from blockchain.utils.hex_to_binary import hex_to_binary


def test_crypto_hash():
	assert crypto_hash(1, "Foo", [3]) == crypto_hash(1, "Foo", [3])
	assert crypto_hash("Bar") == "9cf3754f15467c507012911cc590ee7a571bdb4c6bba30c605868304033db330"


def test_hex_to_binary():
	original_number = 451
	hex_number = hex(original_number)
	binary_number = hex_to_binary(hex_number)
	
	assert int(binary_number, 2) == original_number
