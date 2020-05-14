import json
import hashlib
from classes import Block
from classes import Transaction
from classes import Verification
from hash_util import hash_block
from wallet import Wallet

MINING_REWARD = 10

class Blockchain:
	def __init__(self, public_key, node_id):
		#Genesis block
		genesis_block = Block('', 0, [], 100)
		#initializing the chain
		self.chain = [genesis_block]
		#unhandled transactions
		self.open_transactions = []
		self.node_id = node_id
		self.peer_nodes = set()
		self.load_data()
		self.public_key = public_key

	def load_data(self):
		try:
			with open('blockchain_{}.txt'.format(self.node_id), mode = 'r') as f: #The mode is write and not append (a) because we plan overwriting the data all the time. 
				file_content = f.readlines()
				blockchain = json.loads(file_content[0][:-1])
				updated_blockchain = []
				for block in blockchain:
					converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
					updated_block = Block(block['hash_previous_block'], block['index'], converted_tx, block['proof'], block['timestamp'])
					updated_blockchain.append(updated_block)
				self.chain = updated_blockchain
				open_transactions = json.loads(file_content[1][:-1])
				updated_open_transactions = []
				for transaction in open_transactions:
					updated_transaction = Transaction(transaction['sender'], transaction['recipient'], transaction['signature'], transaction['amount'])
					updated_open_transactions.append(updated_transaction)
				self.open_transactions = updated_open_transactions
				peer_nodes = json.loads(file_content[2])
				self.peer_nodes = set(peer_nodes)
		except (IOError, IndexError):
			pass
		
	def save_data(self):
		try:
			with open('blockchain_{}.txt'.format(self.node_id), mode = 'w') as f: #The mode is write and not append (a) because we plan overwriting the data all the time. 
				saveable_chain = [block.__dict__ for block in [Block(block_el.hash_previous_block, block_el.index, [tx.__dict__ for tx in block_el.transactions] ,block_el.proof, block_el.timestamp) for block_el in self.chain]]
				f.write(json.dumps(saveable_chain)) #we write the blockchain
				f.write('\n') #we jump a line
				saveable_open_transactions = [tx.__dict__ for tx in self.open_transactions]
				f.write(json.dumps(saveable_open_transactions)) #We then write the open transactions
				f.write("\n")
				f.write(json.dumps(list(self.peer_nodes)))
				#The with block statement will close the file automatically
		except IOError:
			print("Error while saving the file")

	def proof_of_work(self):
		last_block = self.chain[-1]
		last_hash = hash_block(last_block)
		proof = 0
		while not Verification.valid_proof(self.open_transactions, last_hash, proof):
			proof += 1
		return proof
	
	def get_balance(self):
		if self.public_key == None:
			return None
		participant = self.public_key
		tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.chain] #stores what the user sents in a list
		open_tx_sender = [tx.amount for tx in self.open_transactions if tx.sender == participant]
		tx_sender.append(open_tx_sender)
		amount_sent = 0
		for tx in tx_sender:
			if len(tx) > 0:
				amount_sent += sum(tx)   #amount_sent is the sum of all the transactions made by this user
		tx_received = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.chain] #stores what the user receives in a list
		amount_received = 0
		for tx in tx_received:
			if len(tx) > 0:
				amount_received += sum(tx)   #amount_s has the sum of all the transactions made by this user
		return amount_received - amount_sent

	def get_last_blockchain_value(self):
		"""get the last value in our blockchain"""
		if len(self.chain) < 1:
			return None
		else:
			return self.chain[-1]

	def get_open_transactions(self):
			"""Returns a copy of the open transactions list."""
			return self.open_transactions[:]
	

	def add_transaction(self, recipient, sender, signature, amount=1.0):
		
		if self.public_key == None:
			return None

		transaction = Transaction(sender, recipient, amount, signature)
		"""if not Wallet.verify_signature(transaction):
			return False"""
		if Verification.verify_transaction(transaction, self.get_balance):
			self.open_transactions.append(transaction)
			self.save_data()
			return True
		else:
			print("Solde insuffisant")
			return False

	def mine_block(self):
		if self.public_key == None:
			return None
			#return False
		if not Verification.verify_chain(self.chain):
			return None
		last_block = self.chain[-1]
		hashed_blocks = hash_block(last_block)
		proof = self.proof_of_work()
		reward_transaction = Transaction('MINING', self.public_key, '', MINING_REWARD)
		copied_transactions = self.open_transactions[:]
		for tx in copied_transactions:
			if not Wallet.verify_signature(tx):
				return None
				#return False
		copied_transactions.append(reward_transaction)
		block = Block(hashed_blocks, len(self.chain), copied_transactions, proof)
		self.chain.append(block)
		self.open_transactions = []
		self.save_data()
		return block
	
	def add_peer_node(self, node):
		"""node: the node url which should be added"""
		self.peer_nodes.add(node)	
		self.save_data()

	
	def remove_peer_node(self, node):
		"""node: the node url which should be removed"""
		self.peer_nodes.discard(node) #Discard removes a value if it is present and does nothing in case it is absent
		self.save_data()
	
	def get_peer_node(self):
		return list(self.peer_nodes)
	

