import uuid

import pytest

from blockchain.core.Blockchain import Blockchain
from blockchain.core.Transaction import Transaction
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


@pytest.fixture
def transaction(wallet):
	recipient_address = uuid.uuid4().hex
	amount = 50
	return Transaction(wallet, recipient_address, amount)


def test_transaction(transaction):
	assert Wallet.verify_signature(
		transaction.input["public_key"],
		dict_to_bytes(transaction.output),
		transaction.input["signature"]
		)


def test_transaction_exceeds_balance(transaction, wallet):
	with pytest.raises(Exception, match="Amount exceeds balance"):
		Transaction(wallet, uuid.uuid4().hex, 10000000)


def test_valid_transaction(transaction):
	Transaction.is_valid(transaction)


def test_valid_transaction_with_invalid_outputs(transaction):
	transaction.output[transaction.input["address"]] = 10000000
	
	with pytest.raises(Exception, match="Invalid transaction"):
		Transaction.is_valid(transaction)


def test_valid_transaction_with_invalid_signature(transaction):
	sender = uuid.uuid4().hex
	keys = generate_wallet_keys()
	blockchain = Blockchain()
	transaction_pool = TransactionPool()
	wallet = Wallet(sender, keys[1], keys[0], blockchain, transaction_pool)
	
	transaction.input["signature"] = wallet.sign(dict_to_bytes(transaction.output))
	
	with pytest.raises(Exception, match="Invalid transaction"):
		Transaction.is_valid(transaction)
