import json
import hashlib
from collections import OrderedDict


MINING_REWARD = 10

blockchain = []
open_transactions = []
owner = "Christopher"
participants = {"Christopher"} #We initialise our set of participants. A set is choosen hier because it takes only unique value and if an existing value wants to be added, then python ignores it
"""Our empty blockchain"""

def load_data():
	global blockchain
	global open_transactions
	try:
		with open('blockchain2.txt', mode = 'r') as f: #The mode is write and not append (a) because we plan overwriting the data all the time. 
			file_content = f.readlines()
			blockchain = json.loads(file_content[0][:-1])
			updated_blockchain = []
			for block in blockchain:
				updated_block = {
					'hash_previous_block' : block['hash_previous_block'], 
					'index' : block['index'],
					'proof' : block['proof'],
					'transactions' : [OrderedDict(
									[('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
					}
				updated_blockchain.append(updated_block)
			blockchain = updated_blockchain
				
			'''updated_blockchain = [{
							'hash_previous_block' : block['hash_previous_block'], 
							'index' : block['index'],
							'transactions' : OrderedDict([
														('sender', block['transactions']['sender']),
														('recipient', block['transactions']['recipient']),
														('amount', block['transactions']['amount'])
														]),
							'proof' : block['proof']} for block in blockchain]
			blockchain = updated_blockchain'''
			open_transactions = json.loads(file_content[1])
			updated_open_transactions = []
			for transaction in open_transactions:
				updated_transaction = OrderedDict(
					[('sender', transaction['sender']), ('recipient', transaction['recipient']), ('amount', transaction['amount'])])
				updated_open_transactions.append(updated_transaction)
			open_transactions = updated_open_transactions
			'''updated_open_transactions = [OrderedDict([
												('sender', transaction['sender']), 
												('recipient', transaction['recipient']), 
												('amount', transaction['amount'])
												]) for transaction in open_transactions]
			open_transactions = updated_open_transactions'''
	except IOError:
		genesis_block = {
		'hash_previous_block':'',
		'index':0,
		'transactions': [],
		'proof': 100
			}
		blockchain = [genesis_block]
		open_transactions = []

load_data()


def save_data():
	try:
		with open('blockchain2.txt', mode = 'w') as f: #The mode is write and not append (a) because we plan overwriting the data all the time. 
			f.write(json.dumps(blockchain)) #we write the blockchain
			f.write('\n') #we jump a line
			f.write(json.dumps(open_transactions)) #We then write the open transactions 
			#The with block statement will close the file automatically
	except IOError:
		print("Error while saving the file")


def get_last_blockchain_value():
	"""get the last value in our blockchain"""
	if len(blockchain) < 1:
		return None
	else:
		return blockchain[-1]


def get_transaction_value():
	"""Asks a transaction amount to the user"""
	tx_recipient = input('Please enter the transaction recipient: ')
	tx_amount = float(input('Please enter the transaction amount: '))
	return (tx_recipient, tx_amount)


def add_transaction(recipient, sender=owner, amount=1.0):
	"""ads the transaction amount as well as the last transaction to the new block"""
	"""The last transaction is default 1"""
	''':sender = the sender of the coins'''
	''':recipient = The recipient of the coins'''
	''':amount = The amount to be sent'''

	''' transaction = {
		'sender':sender,
		'recipient':recipient,
		'amount':amount
	} '''

	transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])


	if verify_transaction(transaction):
		open_transactions.append(transaction)
		participants.add(sender)
		participants.add(recipient) #adds a user to the set of participants and if he already exists, then python ignores it

		save_data()

		return True
	return False

'''def hash_block(block):
	return '-'.join([str(block[key]) for key in block]) #joins table elements as one string of characters seperated with a -'''

def hash_block(block):
	return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

def get_balance(participant):
	tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain] #stores what the user sents in a list
	open_tx_sender = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
	tx_sender.append(open_tx_sender)
	amount_sent = 0
	for tx in tx_sender:
		if len(tx) > 0:
			amount_sent += sum(tx)   #amount_sent is the sum of all the transactions made by this user
	tx_received = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain] #stores what the user receives in a list
	amount_received = 0
	for tx in tx_received:
		if len(tx) > 0:
			amount_received += sum(tx)   #amount_s has the sum of all the transactions made by this user
	return amount_received - amount_sent

def valid_proof(transactions, last_hash, proof):
	'''transactions are the transactions present in the current block'''
	'''This functions returns true if the hash of the three arguments combined contains 2 leading zeros'''
	guess = (str(transactions) + str(last_hash) + str(proof)).encode() #We concatenate our three components and encode them in UTF-8
	guess_hash = hashlib.sha256(guess).hexdigest()
	print(guess_hash)
	return guess_hash[0:3] == '000'

def proof_of_work():
	last_block = blockchain[-1]
	last_hash = hash_block(last_block)
	proof = 0
	while not valid_proof(open_transactions, last_hash, proof):
		proof += 1
	return proof


def mine_block():
	last_block = blockchain[-1]
	hashed_blocks = hash_block(last_block)

	proof = proof_of_work()

	''' reward_transaction = {
						'sender': 'MINING', #The business running the blockchain
						'recipient': owner, #Because the owner is the one mining presently
						'amount': MINING_REWARD
					} ''' 

	reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])


	copied_transactions = open_transactions[:]
	copied_transactions.append(reward_transaction)
	block = {
		'hash_previous_block': hashed_blocks,
		'index':len(blockchain),
		'transactions': copied_transactions,
		'proof': proof
	}
	blockchain.append(block)

	save_data()

	return True


def display_hash():
	for (index, block) in enumerate(blockchain):
		valid_proof(block['transactions'][:-1], block['hash_previous_block'], block['proof']) #[:-1] selects every element in the list except the last one


def verify_chain():
	for (index, block) in enumerate(blockchain):  #enumerate returns the index and the value of each element in a list
		if index == 0:
			continue #We don't want to verify starting from the first block
		if block['hash_previous_block'] != hash_block(blockchain[index-1]):
			return False
		if not valid_proof(block['transactions'][:-1], block['hash_previous_block'], block['proof']): #[:-1] selects every element in the list except the last one
			print("Proof of work is invalid")
			return False
	return True
	'''is_valid = True
	for i in range(len(blockchain)-1):
		if blockchain[i+1][0] == blockchain[i]:
			is_valid = True
		else:
			is_valid = False
			break
	return is_valid'''


def get_user_choice():
	"""Receives the choice of the user between 1 and 2"""
	user_choice = input("Your choice: ")
	return user_choice

def print_blockchain_elements():
	for block in blockchain:
		print('Outputting Block')
		print(block)

def verify_transaction(transaction):
	balance = get_balance(owner)
	return balance >= transaction['amount']

def verify_transactions():
	return all([verify_transaction(trans) for trans in open_transactions])


while True:
	print("Balance of {}: {:6.2f}".format(owner, get_balance(owner)))
	print("Please choose")
	print("1: Add a new transaction value")
	print("2: Mine a new block")
	print("3: Display the blockchain's block")
	print("4: Display the participants")
	print("5: Verify all the chain")
	print("6: Display my balance")
	print("7: Print hash")
	print("h: Manipulate the chain")
	print("q: Quit")
	user_choice = get_user_choice()
	if user_choice == '1':
		tx_data = get_transaction_value()
		recipient, amount = tx_data
		if add_transaction(recipient, amount=amount):
			print("Transaction added!!!")
		else:
			print("Transaction failed!!!")
	elif user_choice == '2':
		if mine_block():
			open_transactions = []
			save_data()
	elif user_choice == '3':
		print_blockchain_elements()
	elif user_choice == '4':
		print(participants)
	elif user_choice == '5':
		if verify_chain():
			print("All transactions are valid")
		else:
			print("There are invalid transactions")
	elif user_choice == '6':
		print(get_balance(owner))
	elif user_choice == '7':
		display_hash()
	elif user_choice == 'h':
		if len(blockchain) > 1:
			blockchain[0] = {
							'hash_previous_block':'',
							'index':0,
							'transactions': {'sender':'Chris', 'Recipient':'Alex', 'amount':500}
						}
	elif user_choice == 'q':
		break
	else:
		print("No Valid input")
	#if not verify_chain():
	#	print("Invalid blockchain!")
	#	break