import json

from blockchain.core.Block import Block


class Blockchain:
	
	def __init__(self):
		self._chain: list[Block] = [Block.genesis()]
	
	def replace_chain(self, chain: list[Block]):
		if len(chain) <= len(self.get_chain()):
			raise Exception('Cannot replace. The incoming chain must be longer')
		
		try:
			Blockchain.is_valid_chain(chain)
		except Exception as e:
			raise Exception(f'Cannot replace. The incoming chain is invalid: {e}')
		
		self._chain = chain
	
	def get_chain(self) -> list[Block]:
		return self._chain
	
	def to_json(self) -> list[str]:
		return list(map(lambda block: block.to_json(), self.get_chain()))
	
	@staticmethod
	def from_json(chain: list) -> list[Block]:
		block_dicts = map(lambda json_block: json.loads(json_block), chain)
		return list(map(lambda block: Block.from_dict(block), block_dicts))
	
	@staticmethod
	def is_valid_chain(chain: list[Block]):
		if chain[0] != Block.genesis():
			raise Exception("The genesis block is not valid")
		
		for i in range(1, len(chain)):
			last_block = chain[i - 1]
			block = chain[i]
			Block.is_valid_block(last_block, block)
