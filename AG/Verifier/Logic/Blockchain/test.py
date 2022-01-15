from web3 import Web3
from UseContract import TransactionContract


w3 = Web3(Web3.HTTPProvider("http://140.125.32.10:8545"))
fa = w3.eth.accounts[1]
ta = w3.eth.accounts[2]


w3 = Web3(Web3.HTTPProvider("http://140.125.32.10:8647"))
AG1 = w3.eth.accounts[0]

w3= Web3(Web3.HTTPProvider("http://140.125.32.10:8747"))
AG2 = w3.eth.accounts[0]


contract = TransactionContract()

contract.ask_for_DeployContraction(AG1,AG2,fa,ta)
contract.setContract(fa,ta,10000000)
contract.setAgreements(fa,ta,True)

