from time import time
from collections import OrderedDict
from hash_util import hash_block
import hashlib
from wallet import Wallet

class Printable:

	def __repr__(self):
		return str(self.__dict__)

class Block(Printable):

	def __init__(self, hash_previous_block, index, transactions, proof, timestamp = None): #The time stamp is set to none because if it was set to time(), then we would had have the same time every time
		self.hash_previous_block = hash_previous_block
		self.index = index
		self.transactions = transactions
		self.proof = proof
		self.timestamp = time() if timestamp is None else timestamp

class Transaction(Printable):

	def __init__(self, sender, recipient, signature, amount):
		self.sender = sender
		self.recipient = recipient
		self.signature = signature
		self.amount = amount

	def ordered_dict(self):
		return OrderedDict([('sender', self.sender),('recipient', self.recipient),('amount', self.amount)])

class Verification:
	@staticmethod
	def valid_proof(transactions, last_hash, proof):
		'''transactions are the transactions present in the current block'''
		'''This functions returns true if the hash of the three arguments combined contains 2 leading zeros'''
		guess = (str([tx.ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode() #We concatenate our three components and encode them in UTF-8
		guess_hash = hashlib.sha256(guess).hexdigest()
		print(guess_hash)
		return guess_hash[0:2] == '00'

	@classmethod
	def verify_chain(cls, blockchain):
		for (index, block) in enumerate(blockchain):  #enumerate returns the index and the value of each element in a list
			if index == 0:
				continue #We don't want to verify starting from the first block
			if block.hash_previous_block != hash_block(blockchain[index-1]):
				return False
			if not cls.valid_proof(block.transactions[:-1], block.hash_previous_block, block.proof): #[:-1] selects every element in the list except the last one
				print("Proof of work is invalid")
				return False
		return True
	
	@staticmethod
	def verify_transaction(transaction, get_balance):
		""":check_funds is to be able to distinguish the verification of the transactions from when we verify 
		the transaction to check for funds or to be sure of the validity"""
		sender_balance = get_balance(transaction.sender)
		return sender_balance >= transaction.amount
 
	@classmethod
	def verify_transactions(cls, open_transactions, get_balance):
		return all([cls.verify_transaction(trans, get_balance) for trans in open_transactions]) #Third argument is False to prevent it from checking the funds