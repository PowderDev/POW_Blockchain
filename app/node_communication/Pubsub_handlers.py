import json
from multiprocessing import Manager

from app import logger
from app.node_communication.MiningProcess import MiningProcess
from blockchain.core.Block import Block
from blockchain.core.Blockchain import Blockchain
from blockchain.core.Transaction import Transaction
from blockchain.core.TransactionPool import TransactionPool


class PubsubHandlers:
	
	@staticmethod
	def block_broadcast(
			json_block: str,
			blockchain: Blockchain,
			transaction_pool: TransactionPool
			) -> None:
		dict_block = json.loads(json_block)
		block = Block.from_dict(dict_block)
		potential_chain = blockchain.get_chain().copy()
		potential_chain.append(block)
		try:
			PubsubHandlers.chain_replacement(blockchain, potential_chain)
			logger.info("Successfully replaced the local chain")
		except Exception as e:
			logger.error(e)
		transaction_pool.clear(blockchain)
		transaction_pool.set_transaction(Transaction.get_reward_transaction(block.miner_address))
	
	@staticmethod
	def new_peer_broadcast(blockchain: Blockchain, potential_chain: list[Block]) -> None:
		PubsubHandlers.chain_replacement(blockchain, potential_chain)
	
	@staticmethod
	def block_mining_broadcast(blockchain: Blockchain, json_data: str, miner_address: str) -> tuple[
		MiningProcess, dict]:
		value_manager = Manager()
		return_dict = value_manager.dict()
		last_block = blockchain.get_chain()[-1]
		
		p = MiningProcess(
			Block.mp_mine_block,
			(last_block, json_data, miner_address, return_dict)
			)
		
		p.start()
		return p, return_dict
	
	@staticmethod
	def chain_replacement(blockchain: Blockchain, potential_chain: list[Block]) -> None:
		blockchain.replace_chain(potential_chain)
