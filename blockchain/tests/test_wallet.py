import uuid

import pytest

from blockchain.core.Blockchain import Blockchain
from blockchain.core.TransactionPool import TransactionPool
from blockchain.core.Wallet import Wallet
from blockchain.utils.dict_to_bytes import dict_to_bytes
from blockchain.utils.generate_wallet_keys import generate_wallet_keys


@pytest.fixture
def wallet():
	sender = uuid.uuid4().hex
	keys = generate_wallet_keys()
	blockchain = Blockchain()
	transaction_pool = TransactionPool()
	return Wallet(sender, keys[1], keys[0], blockchain, transaction_pool)


def test_verify_valid_signature(wallet):
	data = {"foo": "bar"}
	signature = wallet.sign(dict_to_bytes(data))
	assert Wallet.verify_signature(wallet.public_key, dict_to_bytes(data), signature)


def test_verify_invalid_signature(wallet):
	data = {"foo": "bar"}
	signature = wallet.sign(dict_to_bytes(data))
	
	keys = generate_wallet_keys()
	
	assert not Wallet.verify_signature(keys[1], dict_to_bytes(data), signature)
