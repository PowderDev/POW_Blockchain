import asyncio
import json
import uuid
from multiprocessing import Process

import aioredis
import async_timeout

from app import logger
from app.node_communication.Pubsub_broadcasters import PubsubBroadcasters
from app.node_communication.Pubsub_handlers import PubsubHandlers
from app.node_communication.actions import Action
from blockchain.core.Blockchain import Blockchain
from blockchain.core.Transaction import Transaction
from blockchain.core.TransactionPool import TransactionPool


class NodePubsub:
	
	def __init__(
			self,
			url: str,
			channel: str,
			blockchain: Blockchain,
			transaction_pool: TransactionPool
			):
		self.redis = aioredis.from_url(url)
		self.pubsub = self.redis.pubsub()
		self.channel = channel
		self.mining_process: Process | None = None
		self.mined = False
		self.blockchain = blockchain
		self.transaction_pool = transaction_pool
		self.address = uuid.uuid4().hex
		self.broadcasters = PubsubBroadcasters(self.redis, self.channel)
		
		logger.info(
			f" Your miner address is {self.address}."
			f" Mined crypto will be there."
			f" You can easily attach your own waller anytime."
			)
	
	async def listen(self):
		await self.pubsub.subscribe(self.channel)
		await asyncio.create_task(self._reader(self.pubsub))
	
	async def _handle_message_action(self, action: str, json_data: str):
		match action:
			case Action.NEW_BLOCK.value:
				PubsubHandlers.block_broadcast(
					json_data,
					self.blockchain,
					self.transaction_pool
					)
			
			case Action.BLOCK_MINING.value:
				await self._handle_block_mining(json_data)
			
			case Action.BLOCK_MINED.value:
				await self._handle_block_mined(json_data)
			
			case Action.CHAIN_REQUEST.value:
				await self.broadcasters.broadcast_chain_send(json.dumps(self.blockchain.to_json()))
			
			case Action.CHAIN_SEND.value:
				if len(self.blockchain.get_chain()) != 1:
					chain = json.loads(json_data)
					PubsubHandlers.new_peer_broadcast(
						self.blockchain,
						self.blockchain.from_json(chain)
						)
			
			case Action.NEW_TRANSACTION.value:
				transaction = Transaction.from_json(json_data)
				self.transaction_pool.set_transaction(transaction)
	
	async def _handle_block_mining(self, json_data: str):
		self.mined = False
		
		(self.mining_process, return_dict) = PubsubHandlers.block_mining_broadcast(
			self.blockchain,
			json_data,
			self.address
			)
		
		self.mining_process.join()
		
		if not self.mining_process.killed:
			await self.broadcasters.broadcast_block_mined(return_dict["data"])
	
	async def _handle_block_mined(self, json_data: str):
		dict_block = json.loads(json_data)
		
		if not self.mined and dict_block["miner_address"] == self.address:
			await self.broadcasters.broadcast_block_new(json_data)
		
		self.mining_process.kill()
		self.mined = True
	
	async def _reader(self, channel: aioredis.client.PubSub):
		while True:
			try:
				async with async_timeout.timeout(1):
					message = await channel.get_message(ignore_subscribe_messages=True)
					
					if message is not None:
						message_data = json.loads(message["data"])
						action = message_data["action"]
						await self._handle_message_action(action, message_data["data"])
					
					await asyncio.sleep(0.01)
			except asyncio.TimeoutError:
				pass
