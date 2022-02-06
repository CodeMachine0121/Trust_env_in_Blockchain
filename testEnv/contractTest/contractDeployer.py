from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://140.125.32.10:8545"))


with open("Con.json") as file :
    Jdata = json.loads(file.read())

abi = Jdata["abi"]
bytecode = Jdata["bytecode"]

_con = w3.eth.contract(abi=abi,bytecode=bytecode)

txn_body={
    'nonce':w3.eth.getTransactionCount(w3.eth.coinbase),
    'from': w3.eth.coinbase,
    'gas': 10000000

}

result = _con.constructor(w3.eth.coinbase, w3.eth.coinbase).transact({'from':w3.eth.coinbase})

tx_recipt = w3.eth.wait_for_transaction_receipt(result)
address = tx_recipt.contractAddress

# cretaete contract obj
con=w3.eth.contract(abi=abi,address=address)
print("[+] Contracct address: {}".format(address))
print("[+] CA: {}".format(con.functions.getCA().call()))
print("[+] Owner: {}".format(con.functions.getOwner().call()))

AG = w3.eth.coinbase
sender = w3.eth.accounts[1]
recevier = w3.eth.accounts[2]

txn_body["gas"]=100000
txn_body["nonce"]+=1
tx = con.functions.createTransaction(sender,recevier,AG,100,1234).transact(txn_body)

print("Create Transaction ...\n\t{}".format(tx))

print("[+] Owner: {}".format(con.functions.getOwner().call()))

txn_body["nonce"]+=1
tx = con.functions.makePayment(sender,recevier,AG,10,1234).transact(txn_body)
print("Create Payment ...\n\t{}".format(tx))

signature = con.functions.getSignatures(sender,recevier).call()
print("Get Transaction Signature: {}".format(signature))





