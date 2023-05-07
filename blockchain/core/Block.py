import json
import time

from blockchain.constants import MINE_RATE
from blockchain.core.TransactionPool import TransactionPool
from blockchain.utils.hash import crypto_hash
from blockchain.utils.hex_to_binary import hex_to_binary

GENESIS_DATA = {
	'timestamp': 1,
	'last_hash': "Genesis_last_hash",
	'block_hash': "Genesis_hash",
	'transactions': [],
	'difficulty': 1,
	'nonce': 0,
	'miner_address': 1
	}


class Block:
	
	def __init__(
			self,
			timestamp: int,
			last_hash: str,
			block_hash: str,
			transactions: list[dict],
			difficulty: int,
			nonce: int,
			miner_address: str
			):
		self.transactions = transactions
		self.timestamp = timestamp
		self.block_hash = block_hash
		self.last_hash = last_hash
		self.difficulty = difficulty
		self.nonce = nonce
		self.miner_address = miner_address
	
	def __repr__(self):
		return f"[\n Timestamp - {self.timestamp};\n " \
		       f"Hash - {self.block_hash};\n " \
		       f"Nonce - {self.nonce};\n " \
		       f"Difficulty - {self.difficulty}\n]"
	
	def __eq__(self, other: 'Block'):
		return self.block_hash == other.block_hash
	
	def to_json(self):
		return json.dumps(self, default=lambda b: b.__dict__)
	
	@staticmethod
	def from_dict(dict_block: dict) -> 'Block':
		return Block(**dict_block)
	
	@staticmethod
	def mine_block(last_block: 'Block', data: list[str], miner_address: str) -> 'Block':
		last_hash = last_block.block_hash
		timestamp = time.time_ns()
		difficulty = Block.adjust_difficulty(last_block, timestamp)
		nonce = 0
		block_hash = crypto_hash(timestamp, last_hash, data, difficulty, nonce)
		
		while not Block._hash_matches_difficulty(block_hash, difficulty):
			difficulty = Block.adjust_difficulty(last_block, timestamp)
			nonce += 1
			timestamp = time.time_ns()
			block_hash = crypto_hash(timestamp, last_hash, data, difficulty, nonce)
		
		transaction_dicts = TransactionPool.from_json_to_dicts(data)
		return Block(
			timestamp,
			last_hash,
			block_hash,
			transaction_dicts,
			difficulty,
			nonce,
			miner_address
			)
	
	@staticmethod
	def mp_mine_block(
			last_block: 'Block',
			data: list[str],
			miner_address: str,
			return_dict: dict
			) -> None:
		return_dict["data"] = Block.mine_block(last_block, data, miner_address)
	
	@staticmethod
	def adjust_difficulty(last_block: 'Block', new_block_timestamp: int) -> int:
		if (new_block_timestamp - last_block.timestamp) < MINE_RATE:
			return last_block.difficulty + 1
		
		if last_block.difficulty - 1 == 0:
			return 1
		
		return last_block.difficulty - 1
	
	@staticmethod
	def is_valid_block(last_block: 'Block', block: 'Block') -> bool:
		if block.last_hash != last_block.block_hash:
			raise Exception("The block last_hash is not equal to the last block hash")
		
		if not Block._hash_matches_difficulty(block.block_hash, block.difficulty):
			raise Exception("The proof of requirement was not met")
		
		if abs(last_block.difficulty - block.difficulty) > 1:
			raise Exception("The block difficulty must only adjust by 1")
		
		json_transactions = list(map(lambda t: json.dumps(t), block.transactions))
		
		reconstructed_hash = crypto_hash(
			block.timestamp,
			block.last_hash,
			json_transactions,
			block.difficulty,
			block.nonce
			)
		
		if block.block_hash != reconstructed_hash:
			raise Exception("The block hash is not correct")
		
		return True
	
	@staticmethod
	def _hash_matches_difficulty(block_hash: str, difficulty: int) -> bool:
		leading_zeros = hex_to_binary(block_hash)[0:difficulty]
		return leading_zeros == '0' * difficulty
	
	@staticmethod
	def genesis() -> 'Block':
		return Block(**GENESIS_DATA)
