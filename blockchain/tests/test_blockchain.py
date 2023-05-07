import uuid

import pytest

from blockchain.core.Block import GENESIS_DATA, Block
from blockchain.core.Blockchain import Blockchain
from blockchain.core.Transaction import Transaction
from blockchain.core.TransactionPool import TransactionPool
from blockchain.core.Wallet import Wallet
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


def test_blockchain_genesis():
	blockchain = Blockchain()
	assert blockchain.get_chain()[0].block_hash == GENESIS_DATA['block_hash']


@pytest.fixture()
def blockchain(transaction):
	blockchain = Blockchain()
	
	for i in range(3):
		block = Block.mine_block(blockchain.get_chain()[-1], [], "0x")
		potential_chain = blockchain.get_chain().copy()
		potential_chain.append(block)
		blockchain.replace_chain(potential_chain)
	
	return blockchain


def test_is_valid_chain():
	blockchain = Blockchain()
	Blockchain.is_valid_chain(blockchain.get_chain())


def test_is_valid_chain_bad_genesis():
	blockchain = Blockchain()
	blockchain.get_chain()[0].block_hash = "bad"
	
	with pytest.raises(Exception, match="The genesis block is not valid"):
		Blockchain.is_valid_chain(blockchain.get_chain())


def test_replace_chain(blockchain):
	print(len(blockchain.get_chain()))
	new_blockchain = Blockchain()
	new_blockchain.replace_chain(blockchain.get_chain())
	
	assert new_blockchain.get_chain() == blockchain.get_chain()


def test_replace_chain_not_longer(blockchain):
	new_blockchain = Blockchain()
	with pytest.raises(Exception, match="The incoming chain must be longer"):
		blockchain.replace_chain(new_blockchain.get_chain())


def test_replace_chain_bad_chain(blockchain):
	new_blockchain = Blockchain()
	blockchain.get_chain()[1].block_hash = "bad"
	
	with pytest.raises(Exception, match="The incoming chain is invalid"):
		new_blockchain.replace_chain(blockchain.get_chain())
