import time

from blockchain.constants import SECONDS
from blockchain.core.Block import Block
from blockchain.core.Blockchain import Blockchain

times = []
blockchain = Blockchain()

for i in range(1000):
	start_time = time.time_ns()
	block = Block.mine_block(blockchain.get_chain()[-1], [], "0x")
	potential_chain = blockchain.get_chain()
	potential_chain.append(block)
	blockchain.replace_chain(potential_chain)
	end_time = time.time_ns()
	
	time_to_mine = (end_time - start_time) / SECONDS
	times.append(time_to_mine)
	
	average_time = sum(times) / len(times)
	
	print(f"New block difficulty: {blockchain.get_chain()[-1].difficulty}")
	print(f"Time took to mine new block: {time_to_mine}s")
	print(f"Average time to add new blocks: {average_time}s\n\n")
