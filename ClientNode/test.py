from Client import Client
from web3 import Web3
import time

w3 = Web3()

client = Client('http://192.168.50.190:8888')
# client.RegisterAG()

# client.ask_for_Client_available(client.address)
# client.askTransaction(client.address,acc,10)
if __name__ == '__main__':

    fromAG = ""
    while True:
        command = input("command: ")

        if command == "reg":
            print("[+] Registering Phase ")
            try:
                Name = str(input("\t[-] Name: "))
                liveAddress = str(input("\t[-] Living Address: "))
                Id = str(input("\t[-] ID Number: "))
                phoneNumber = str(input("\t[-] Phone Number: "))
                email = str(input("\t[-] Email: "))

            except Exception as e:
                print("\t[!] 錯誤輸入: {}".format(repr(e)))
                continue

            userData = {
                "Id": Id,
                "Name": Name,
                "liveAddress": liveAddress,
                "phoneNumber": phoneNumber,
                "email": email,
            }

            client.RegisterAG(userData)

        elif command == "balance":
            print("[+] Get Balance Phase: ")
            try:
                acc = w3.toChecksumAddress(input("\t[-]Receiver: "))
            except:
                print("[!] 輸入錯誤")
                continue
            totalAmount, payedAmount = client.getBalance(client.address, acc)
            print("\t[-] 可使用: ", totalAmount)
            print("\t[-] 已使用: ", payedAmount)

        elif command == "transaction":
            try:
                acc = w3.toChecksumAddress(input("\t[-] Receiver: "))
                amount = w3.toWei(float(input("\t[-]Balance (eth): ")), 'ether')
            except:
                print("[!] 輸入錯誤")
                continue
            start = time.time()
            client.askTransaction(client.address, acc, amount)
            print("[+] 花費時間: {}".format(time.time() - start))

        elif command == "payment":
            try:
                acc = w3.toChecksumAddress(input("\t[-] Receiver: "))
                amount = w3.toWei(float(input("\t[-] Balance: ")), 'ether')
            except:
                print("[!] 輸入錯誤")
                continue

            start = time.time()
            client.payment(client.address, acc, amount)
            print("[+] 花費時間: {}".format(time.time() - start))

        elif command == "payCheck":
            print("[+] Receiver payment Phase")
            try:
                from_address = w3.toChecksumAddress(input("\t[-] Sender: "))
                balance = float(input("\t[-] Balance: "))
                client.receivePayment(from_address, balance)
            except Exception as e:
                print("\t[-] 輸入錯誤: {}".format(repr(e)))

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
                data["paymentSign"] = int(input("\t[-] Payment Signature: "), 16)

                start = time.time()
                client.withdraw_from_Contract(txn, txnCH, contractAddr, senderAGAddr, data)
                print("[+] 花費時間: {}".format(time.time() - start))

            except Exception as e:
                print("[!] 輸入錯誤: {}".format(repr(e)))
                continue
        elif command == "performance":
            times = int(input("\t[-] 次數: "))
            to_addr = w3.toChecksumAddress(input("\t[-] Receiver's Address: "))
            balance = int(w3.toWei(float(input("\t[-] Balance: ")), 'ether'))

            start = time.time()
            client.PerformanceTesting(times, to_addr, balance)
            print("--------------------------------------------------------------")
            print("共耗時: {} sec".format(time.time() - start))
        elif command == "normalTransaction":
            times = int(input("\t[-] 次數: "))
            to_addr = w3.toChecksumAddress(input("\t[-] Receiver's Address: "))
            balance = int(w3.toWei(float(input("\t[-] Balance: ")), 'ether'))
            client.TransactionTesting(times, to_addr, balance)
        elif command == "withdrawTesting":
            client.withdrawTesting()
        elif command == "refresh":
            client.refreshSessionKey()
        elif command == "quit":
            client.quit_current_AG()
    # client.quit_current_AG()
    print()
