import time
import uuid

import pytest

from blockchain.constants import SECONDS, MINE_RATE
from blockchain.core.Block import Block, GENESIS_DATA
from blockchain.core.Blockchain import Blockchain
from blockchain.core.Transaction import Transaction
from blockchain.core.TransactionPool import TransactionPool
from blockchain.core.Wallet import Wallet
from blockchain.utils.generate_wallet_keys import generate_wallet_keys
from blockchain.utils.hex_to_binary import hex_to_binary


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


def test_mine_block(transaction):
	last_block = Block.genesis()
	data = [transaction.to_json()]
	miner_address = "0xa50"
	block = Block.mine_block(last_block, data, miner_address)
	
	assert isinstance(block, Block)
	assert block.last_hash == last_block.block_hash
	assert hex_to_binary(block.block_hash)[0:block.difficulty] == "0" * block.difficulty


def test_genesis():
	genesis = Block.genesis()
	
	assert isinstance(genesis, Block)
	for key, value in GENESIS_DATA.items():
		assert getattr(genesis, key) == value


def test_quickly_mined_block(transaction):
	data = [transaction.to_json()]
	miner_address = "0xa50"
	last_block = Block.mine_block(Block.genesis(), data, miner_address)
	mined_block = Block.mine_block(last_block, data, miner_address)
	
	assert mined_block.difficulty == last_block.difficulty + 1


def test_slowly_mined_block(transaction):
	data = [transaction.to_json()]
	miner_address = "0xa50"
	last_block = Block.mine_block(Block.genesis(), data, miner_address)
	time.sleep(MINE_RATE / SECONDS)
	mined_block = Block.mine_block(last_block, data, miner_address)
	
	# Since genesis block difficulty is 1, last_block's also will be 1.
	# So we are checking if the difficulty of the new block is increased,
	# which should not
	assert mined_block.difficulty == last_block.difficulty
	
	# Here we are checking if the last_block indeed has the difficulty of 1
	# and the new block's difficulty has not gone below zero or equals zero
	assert mined_block.difficulty == 1


@pytest.fixture()
def last_block():
	return Block.genesis()


@pytest.fixture()
def block(last_block, transaction):
	miner_address = "0xa50"
	return Block.mine_block(last_block, [transaction.to_json()], miner_address)


def test_is_valid_block(last_block, block):
	Block.is_valid_block(last_block, block)


def test_is_valid_block_bad_last_hash(last_block, block):
	block.last_hash = "corrupted"
	
	with pytest.raises(Exception, match="last_hash is not equal to the last block hash"):
		Block.is_valid_block(last_block, block)


def test_is_valid_block_bad_proof_of_work(last_block, block):
	block.block_hash = "bad"
	
	with pytest.raises(Exception, match="The proof of requirement was not met"):
		Block.is_valid_block(last_block, block)


def test_is_valid_block_bad_difficulty_adjust(last_block, block):
	wrong_difficulty = 20
	block.difficulty = wrong_difficulty
	block.block_hash = f"{'0' * wrong_difficulty}aaaa"
	
	with pytest.raises(Exception, match="The block difficulty must only adjust by 1"):
		Block.is_valid_block(last_block, block)


def test_is_valid_block_bad_block_hash(last_block, block):
	block.block_hash = "000000000000000000000aaaa"
	
	with pytest.raises(Exception, match="The block hash is not correct"):
		Block.is_valid_block(last_block, block)
