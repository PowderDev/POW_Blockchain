import json
import time
import uuid

from cryptography.hazmat.primitives.asymmetric.utils import (
	decode_dss_signature,
	encode_dss_signature
	)

from blockchain.constants import MINING_REWARD
from blockchain.core.Wallet import Wallet
from blockchain.utils.dict_to_bytes import dict_to_bytes


class Transaction:
	def __init__(
			self,
			sender_wallet: Wallet = None,
			recipient_address: str = None,
			amount: int = None,
			id=None,
			output=None,
			input=None
			):
		# The use of Nones above if coming from the ability of
		# instance of Transaction class to convert to json and back
		
		if not id or not input or not output:
			self._validate_on_init(amount, sender_wallet, recipient_address)
		
		self.id = id or uuid.uuid4().hex
		self.output = output or self._create_output(sender_wallet, recipient_address, amount)
		self.input = input or self._create_input(sender_wallet)
	
	def _create_output(self, sender_wallet: Wallet, recipient_address: str, amount: int):
		return {
			recipient_address: amount,
			sender_wallet.address: sender_wallet.balance - amount
			}
	
	def _create_input(self, sender_wallet: Wallet):
		return {
			"timestamp": time.time_ns(),
			"amount": sender_wallet.balance,
			"address": sender_wallet.address,
			"public_key": sender_wallet.public_key,
			"signature": sender_wallet.sign(dict_to_bytes(self.output))
			}
	
	def _validate_on_init(self, amount: int, sender_wallet: Wallet, recipient_address: str) -> None:
		if not amount or not sender_wallet or not recipient_address:
			raise Exception("Not all required fields were provided")
		
		if amount > sender_wallet.balance:
			raise Exception("Amount exceeds balance")
	
	def _validate_on_update(self, sender_wallet: Wallet, amount: int) -> None:
		if amount > self.output.get(sender_wallet.address, 0):
			raise Exception("Amount exceeds balance")
	
	def to_dict(self) -> dict:
		# Cannot make deepcopy
		self_dict = self.__dict__.copy()
		self_dict['input'] = self_dict['input'].copy()
		
		# Exception will be fired on every mining reward transaction
		try:
			pk = self_dict["input"]["public_key"]
			s = self_dict["input"]["signature"]
			self_dict["input"]["public_key"] = Wallet.get_serialized_public_key(pk)
			self_dict["input"]["signature"] = decode_dss_signature(s)
		except KeyError:
			pass
		
		return self_dict
	
	def to_json(self) -> str:
		return json.dumps(self.to_dict())
	
	@staticmethod
	def from_json(json_data: str) -> 'Transaction':
		transaction_dict = json.loads(json_data)
		return Transaction.from_dict(transaction_dict)
	
	@staticmethod
	def from_dict(dict_data: dict) -> 'Transaction':
		pk = dict_data["input"]["public_key"]
		s = dict_data["input"]["signature"]
		dict_data["input"]["public_key"] = Wallet.get_deserialized_public_key(pk)
		dict_data["input"]["signature"] = encode_dss_signature(s[0], s[1])
		
		return Transaction(**dict_data)
	
	@staticmethod
	def is_valid(transaction: 'Transaction') -> None:
		output_total = sum(transaction.output.values())
		
		if transaction.input["amount"] != output_total:
			raise Exception("Invalid transaction output values")
		
		if not Wallet.verify_signature(
				transaction.input["public_key"],
				dict_to_bytes(transaction.output),
				transaction.input["signature"]
				):
			raise Exception("Invalid transaction signature")
	
	@staticmethod
	def get_reward_transaction(miner_address: str):
		output = {
			miner_address: MINING_REWARD
			}
		input = {
			'address': "*--MINING_REWARD_GIVER--*"
			}
		return Transaction(input=input, output=output, id="0xthanks_for_new_block")
