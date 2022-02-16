from Client import Client
from web3 import Web3

w3 = Web3()


client = Client('http://0.0.0.0:8888')
#client.RegisterAG()

#client.ask_for_Client_available(client.address)
#client.askTransaction(client.address,acc,10)
fromAG = ""
while True:
    command = input("command: ")

    if command == "reg":
        client.RegisterAG()
    elif command == "askAvailable":
        client.ask_for_Client_available(client.address)
    elif command == "balance":
        print("[+] Getting Balance information: ")
        acc = input("\t[-]Receiver: ")
        client.getContractBalance(client.address, acc)
    elif command == "transaction":
        acc = w3.toChecksumAddress(input("\t[-] Receiver: "))
        amount = int(input("\t[-]Balance: "))
        client.askTransaction(client.address,acc,amount)
    elif command == "payment":
        acc = w3.toChecksumAddress(input("\t[-] Receiver: "))
        amount = int(input("\t[-] Balance: "))
        client.payment(client.address, acc, amount)
    elif command == "setContract":
        acc = w3.toChecksumAddress(input("\t[-] Sender: "))
        fromAG = client.setTransactionContract(acc)

    elif command == "terminateTransaction":
        acc = w3.toChecksumAddress(input("\t[-] Sender: "))
        client.terminateTransaction(fromAG, acc, client.address)
    elif command == "quit":
        client.quit_current_AG()
#client.quit_current_AG()
print()   
