import asyncio
import os
import uuid

import dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.node_communication.Pubsub import NodePubsub
from blockchain.core.Blockchain import Blockchain
from blockchain.core.Transaction import Transaction
from blockchain.core.TransactionPool import TransactionPool
from blockchain.core.Wallet import Wallet
from blockchain.utils.generate_wallet_keys import generate_wallet_keys

dotenv.load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
REDIS_BLOCKCHAIN_CHANNEL = os.getenv("REDIS_BLOCKCHAIN_CHANNEL")

app = FastAPI()

blockchain = Blockchain()
transaction_pool = TransactionPool()
pubsub = NodePubsub(REDIS_URL, REDIS_BLOCKCHAIN_CHANNEL, blockchain, transaction_pool)


@app.on_event("startup")
async def startup():
	asyncio.create_task(pubsub.listen())
	await pubsub.broadcasters.broadcast_chain_request()


@app.get('/blockchain')
async def route_blockchain_chain():
	return blockchain.get_chain()


@app.get('/wallet/generate')
async def route_blockchain_chain():
	keys = generate_wallet_keys()
	private_key_string = Wallet.get_serialized_private_key(keys[0])
	public_key_string = Wallet.get_serialized_public_key(keys[1])
	
	address = uuid.uuid4().hex
	return {
		"private_key": private_key_string,
		"public_key": public_key_string,
		"address": address
		}


class GetWalletBalance(BaseModel):
	address: str
	public_key: str
	private_key: str


@app.get("/wallet/balance")
async def route_wallet_info(body: GetWalletBalance):
	public_key = Wallet.get_deserialized_public_key(body.public_key)
	private_key = Wallet.get_deserialized_private_key(body.private_key)
	
	wallet = Wallet(body.address, public_key, private_key, blockchain, transaction_pool)
	return wallet.balance


@app.post('/blockchain/mine')
async def route_blockchain_mine():
	transaction_pool_data = transaction_pool.to_json()
	await pubsub.broadcasters.broadcast_block_mining(transaction_pool_data)


class TransactionBody(BaseModel):
	recipient: str
	amount: int
	sender: str
	public_key: str
	private_key: str


@app.post("/transact")
async def route_transact(body: TransactionBody):
	public_key = Wallet.get_deserialized_public_key(body.public_key)
	private_key = Wallet.get_deserialized_private_key(body.private_key)
	
	sender_wallet = Wallet(body.sender, public_key, private_key, blockchain, transaction_pool)
	
	try:
		transaction = Transaction(sender_wallet, body.recipient, body.amount)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"{e}")
	
	await pubsub.broadcasters.broadcast_transaction_new(transaction)
	return transaction.to_dict()
