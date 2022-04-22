from Client import Client
from web3 import Web3

w3 = Web3()


client = Client('http://192.168.50.184:8888')
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
        try:
            acc = w3.toChecksumAddress(input("\t[-]Receiver: "))
        except:
            print("[!] 輸入錯誤")
            continue
        client.getContractBalance(client.address, acc)
    
    elif command == "transaction":
        try:
            acc = w3.toChecksumAddress(input("\t[-] Receiver: "))
            amount = w3.toWei(float(input("\t[-]Balance (eth): ")), 'ether')
        except:
            print("[!] 輸入錯誤")
            continue
        client.askTransaction(client.address,acc,amount)
    
    elif command == "payment":
        try:
            acc = w3.toChecksumAddress(input("\t[-] Receiver: "))
            amount = w3.toWei(float(input("\t[-] Balance: ")),'ether')
        except:
            print("[!] 輸入錯誤")
            continue
        client.payment(client.address, acc, amount)
    
    elif command == "withdraw":
        try:
           # txn, txnCH, contractAddr, data, senderPubX, senderPubY
            txn = input("\t[-] Contract Action txn: ")
            txnCH = input("\t[-] Signature txn: ")
            contractAddr = w3.toChecksumAddress(input("\t[-] Contract Addr: "))
            senderAGAddr = w3.toChecksumAddress(input("\t[-] Sender AG Address: "))
            

            data = dict()
            data["from_address"] = w3.toChecksumAddress(input("\t[-] Sender's Address: "))
            data["balance"] = w3.toWei(float(input("\t[-] Balance(eth): ")), 'ether')
            data["paymentSign"] = int(input("\t[-] Payment Signature: "),16)
            client.withdraw_from_Contract(txn, txnCH, contractAddr, senderAGAddr, data)

        except Exception as e:
            print("[!] 輸入錯誤: {}".format(repr(e)))
            continue
    elif command == "quit":
        client.quit_current_AG()
#client.quit_current_AG()
print()   
