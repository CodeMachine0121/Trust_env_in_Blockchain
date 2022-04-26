from Client import Client
from web3 import Web3
import time


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
        start = time.time()
        client.askTransaction(client.address,acc,amount)
        print("[+] 花費時間: {}".format(time.time()-start))

    elif command == "payment":
        try:
            acc = w3.toChecksumAddress(input("\t[-] Receiver: "))
            amount = w3.toWei(float(input("\t[-] Balance: ")),'ether')
        except:
            print("[!] 輸入錯誤")
            continue

        start = time.time()
        client.payment(client.address, acc, amount)
        print("[+] 花費時間: {}".format(time.time()-start))
        
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
            
            start = time.time()
            client.withdraw_from_Contract(txn, txnCH, contractAddr, senderAGAddr, data)
            print("[+] 花費時間: {}".format(time.time()-start))

        except Exception as e:
            print("[!] 輸入錯誤: {}".format(repr(e)))
            continue
    elif command == "performance":
        from_addr = w3.toChecksumAddress(input("\t[-] Sender's Address: "))
        to_addr = w3.toChecksumAddress(input("\t[-] Receiver's Address: "))
        balance = w3.toWei(float(input("\t[-] Balance: ")), 'ether')
        
        start = time.time()
        client.PerformanceTesting(from_addr, to_addr, balance)
        print("--------------------------------------------------------------")
        print("共耗時: {} sec".format(time.time()-start))
    elif command == "quit":
        client.quit_current_AG()
#client.quit_current_AG()
print()   
