from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import (
	EllipticCurvePublicKey,
	EllipticCurvePrivateKey
	)

from blockchain.constants import STARTING_AMOUNT


class Wallet:
	hashing_algorithm = ec.ECDSA(hashes.SHA256())
	
	def __init__(
			self,
			address: str,
			public_key: EllipticCurvePublicKey,
			private_key: EllipticCurvePrivateKey,
			blockchain,
			transaction_pool
			):
		self.private_key = private_key
		self.public_key = public_key
		self.address = address
		self.balance = self.calculate_balance(blockchain, transaction_pool, address)
	
	def sign(self, data: bytes) -> bytes:
		return self.private_key.sign(data, Wallet.hashing_algorithm)
	
	@staticmethod
	def get_serialized_public_key(public_key: EllipticCurvePublicKey) -> str:
		public_bytes = public_key.public_bytes(
			serialization.Encoding.PEM,
			serialization.PublicFormat.SubjectPublicKeyInfo
			)
		
		public_sting = public_bytes.decode("utf-8")
		return public_sting
	
	@staticmethod
	def get_deserialized_public_key(public_key: str):
		return serialization.load_pem_public_key(public_key.encode("utf-8"), default_backend())
	
	@staticmethod
	def get_serialized_private_key(private_key: EllipticCurvePrivateKey) -> str:
		private_bytes = private_key.private_bytes(
			serialization.Encoding.PEM,
			serialization.PrivateFormat.PKCS8,
			serialization.NoEncryption(),
			)
		
		private_sting = private_bytes.decode("utf-8")
		return private_sting
	
	@staticmethod
	def get_deserialized_private_key(private_key: str):
		return serialization.load_pem_private_key(
			private_key.encode("utf-8"),
			None,
			default_backend()
			)
	
	@staticmethod
	def verify_signature(public_key: EllipticCurvePublicKey, data: bytes, signature: bytes) -> bool:
		try:
			public_key.verify(signature, data, Wallet.hashing_algorithm)
			return True
		except InvalidSignature:
			return False
	
	@staticmethod
	def calculate_balance(blockchain, transaction_pool, address: str):
		balance = STARTING_AMOUNT
		
		for block in blockchain.get_chain():
			for transaction in block.transactions:
				if transaction['input']['address'] == address:
					balance = transaction['output'][address]
				elif address in transaction['output']:
					balance += transaction.output[address]
		
		for transaction in transaction_pool.transaction_map.values():
			if transaction.input['address'] == address:
				balance = transaction.output[address]
			elif address in transaction.output:
				balance += transaction.output[address]
		
		return balance
