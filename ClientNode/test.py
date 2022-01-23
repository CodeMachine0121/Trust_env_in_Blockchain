from Client import Client
from web3 import Web3

w3 = Web3()
acc = w3.toChecksumAddress('0fa5c5cc08f2d19e70c2fccaf211f2bb5408150e')


client = Client('http://140.125.32.10:8888')
client.RegisterAG()
client.ask_for_Client_available(client.address)
client.askTransaction(client.address,acc,10)
client.payment(client.address, acc, 1)
client.quit_current_AG()
print()   
