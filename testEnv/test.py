from web3 import Web3
import json

blockchain_address = 'http://140.125.32.10:8545'

web3 = Web3(Web3.HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]


compiled_contract_path = 'build/contract/'





