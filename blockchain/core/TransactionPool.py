import json

from blockchain.core.Transaction import Transaction


class TransactionPool:
	def __init__(self):
		self.transaction_map: dict[Transaction] = {}
	
	def set_transaction(self, transaction: Transaction):
		self.transaction_map[transaction.id] = transaction
	
	def clear(self, blockchain):
		for block in blockchain.get_chain()[-1:]:
			if len(self.transaction_map.values()) == 0:
				break
			
			for transaction in block.transactions:
				try:
					del self.transaction_map[transaction['id']]
				except KeyError:
					pass
	
	def to_json(self) -> list[str]:
		return list(map(lambda t: t.to_json(), self.transaction_map.values()))
	
	@staticmethod
	def from_json_to_dicts(transactions: list[str]) -> list[dict]:
		return list(map(lambda t: json.loads(t), transactions))
