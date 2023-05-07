import json

from aioredis import Redis

from app import logger
from app.node_communication.actions import Action
from blockchain.core.Block import Block
from blockchain.core.Transaction import Transaction


class PubsubBroadcasters:
	def __init__(self, redis: Redis, channel: str):
		self.redis = redis
		self.channel = channel
	
	async def broadcast_block_new(self, json_block: str):
		logger.info("You mined the new block. Broadcasting...")
		await self._publish(Action.NEW_BLOCK.value, json_block)
	
	async def broadcast_block_mining(self, data: list[str]):
		await self._publish(Action.BLOCK_MINING.value, data)
	
	async def broadcast_block_mined(self, block: Block):
		await self._publish(Action.BLOCK_MINED.value, block.to_json())
	
	async def broadcast_chain_request(self):
		logger.info("Broadcasting request for the current chain")
		await self._publish(Action.CHAIN_REQUEST.value)
	
	async def broadcast_chain_send(self, json_chain: str):
		await self._publish(Action.CHAIN_SEND.value, json_chain)
	
	async def broadcast_transaction_new(self, transaction: Transaction):
		logger.info("Broadcasting new transaction")
		await self._publish(Action.NEW_TRANSACTION.value, transaction.to_json())
	
	async def _publish(self, action: str, data=None):
		message_data = {"action": action, "data": data}
		await self.redis.publish(self.channel, json.dumps(message_data))
