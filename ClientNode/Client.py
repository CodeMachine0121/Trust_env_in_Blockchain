import requests
import os
import json
from web3 import Web3
# from web3.middleware import geth_poa_middleware
from Crypto.Random.random import getrandbits
from ecc.curve import Point, secp256k1
import time
from Lib.ChameleonShort.Participator import Participator
from Lib.CipherAlgorithm import AES_Library as AES


def getPrivateKey(web3):
    keyfile = os.listdir("./Lib/Blockchain/keystore")[0]
    with open(os.path.join("./Lib/Blockchain/keystore", keyfile)) as file:
        encrypted_key = file.read()
        privateKey = web3.eth.account.decrypt(encrypted_key, "mcuite")
    return privateKey


def getServerAddress():
    # 讀取 server.json: 上面記錄用戶節點的URL
    with open("./Lib/Blockchain/server.json") as file:
        nodeServer = json.loads(file.read())["nodeServer"]
    return nodeServer


def getAddress():
    w3 = Web3()
    path = ""
    for file in os.listdir("./Lib/Blockchain/keystore"):
        path = os.path.join('./Lib/Blockchain/keystore', file)

    with open(path) as f:
        priv = w3.eth.account.decrypt(f.read(), "mcuite")

    acct = w3.eth.account.privateKeyToAccount(priv)

    return w3.toChecksumAddress(acct.address)


class Client:
    def __init__(self, server):
        self.server = server
        print("[+] Getting System Parameters")
        res = requests.get('{}/AG/Parameters/'.format(server))
        Jsystem = json.loads(res.text)

        self.Public_AG = Point(Jsystem.get("Knx"), Jsystem.get("Kny"), curve=secp256k1)

        self.part = Participator()
        self.agAddr = None
        self.contract = None
        self.nodeServer = getServerAddress()

        self.w3 = Web3(Web3.HTTPProvider(self.nodeServer))
        # self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.abi = self.getABI()
        self.address = getAddress()
        self.nonce = self.w3.eth.getTransactionCount(self.address)

        self.paymentRecord = dict()  # 紀錄支付名單
        self.optAns = None

    ## 讀取ABI
    def getABI(self, ):
        try:
            abi = ""
            with open("TransferContract.json", 'r') as file:
                abi = json.loads(file.read())["abi"]
            return abi
        except Exception as e:
            print(repr(e))
            print("找不到 abi file")

    ## 更換server
    def Refresh_AG(self, server):
        self.__init__(server)

    ## 設定 Session Key
    def RegisterAG(self, userData):
        ## One Time Password Authentication
        userData["chainAddress"] = self.address
        res = requests.post("{}/AG/Register/".format(self.server),
                            data=json.dumps(userData))
        if res.status_code != 200:
            print("[!] Something Error!")
        print("[+] The OTP has already send to you as SMS message please check it")
        self.optAns = str(input("\t[-] Your OTP: "))

        ## Session key Exchange
        ## 計算 zP
        z = int(getrandbits(128))
        zp = self.part.P * z
        zpX = zp.x
        zpY = zp.y
        while True:
            res = requests.post('{}/AG/SessionKey/'.format(self.server),
                                data=json.dumps({
                                    'otpAnswer': self.optAns,
                                    'phoneNumber': userData["phoneNumber"],
                                    'zpX': zpX,
                                    'zpY': zpY,
                                    'KnX': int(self.part.Kn.x),
                                    'address': self.address
                                }))
            result = dict(json.loads(res.text))
            if "result" in result.keys():
                print("[!] {}".format(result["result"]))
                if result["result"] == "Already registered":
                    return
                elif result["result"] == "OPT Authentication Failed":
                    ans = input("\t[-] Resend (y/n) ")
                    if ans == "y":
                        res = requests.post("{}/AG/ResendOTP/".format(self.server),
                                            data=json.dumps({
                                                "phoneNumber": userData["phoneNumber"]}))
                        print("[+] The OTP has already send to ur Email, please check it")
                        self.optAns = str(input("\t[-] Your OTP: "))
                        continue
                    else:
                        print("[!] Quit the Registering Phase! ")
                        return
            else:
                break

        xpX = json.loads(res.text).get('xPX')
        xpY = json.loads(res.text).get('xPY')
        self.agAddr = json.loads(res.text).get("address")

        ### 計算sk
        self.part.start_SessionKey(z, xpX, xpY, self.optAns)
        print("\t[-] 完成註冊")
        return

    def refreshSessionKey(self):
        print("[+] Refresh Session Key: ")
        z = int(getrandbits(128))
        zp = self.part.P * z
        zpX = zp.x
        zpY = zp.y
        res = requests.post("{}/AG/updateSessionKey/".format(self.server),
                            data=json.dumps(
                                {"zpX": zpX, "zpY": zpY, "address": self.address, "cliPub": self.part.Kn.x}))
        if 'result' in dict(json.loads(res.text)).keys():
            print("[!] {}".format(json.loads(res.text)['result']))
            return

        xpX = json.loads(res.text).get("xpX")
        xpY = json.loads(res.text).get("xpY")
        ## 重新計算sk
        self.part.start_SessionKey(z, xpX, xpY, self.optAns)
        return

    ## 開啟通道、支付時使用
    def beforeAction(self, from_address, to_address, balance):
        ### 簽章驗證
        msg = str(from_address) + ":" + str(to_address) + ":" + str(balance)
        key = self.part.sk
        en_msg, iv = AES.Encrypt(key, msg)
        # en_msg = self.rsa.EncryptFunc(msg, self.AG_RSA_PublicKey)
        # en_from_address = self.rsa.EncryptFunc(str(from_address), self.AG_RSA_PublicKey)
        # en_to_address = self.rsa.EncryptFunc(str(to_address), self.AG_RSA_PublicKey)
        # en_balance = self.rsa.EncryptFunc(str(balance), self.AG_RSA_PublicKey)
        r = self.part.MakeSignature(msg)
        data = {
            "msg": en_msg,
            "iv": iv,
            "r": r,
            "Knx": int(self.part.Kn.x),
            "Kny": int(self.part.Kn.y),
            "chainAddress": self.address,
        }
        self.part.refreshSignatureKey()
        return data

    # 退出現在的AG
    def quit_current_AG(self):

        msg = str(self.address)
        en_msg, iv = AES.Encrypt(self.part.sk, msg)
        r = self.part.MakeSignature(msg)

        # print("[Debug]: {}".format(en_msg))
        data = {
            "msg": en_msg,
            "iv": iv,
            "r": r,
            "Knx": int(self.part.Kn.x),
            "Kny": int(self.part.Kn.y),
            "chainAddress": self.address,
        }

        # data = self.beforeAction(str(self.address)+ str(self.part.sk))
        res = requests.post("{}/AG/quit_AG/".format(self.server), data=json.dumps(data))
        print("[+] Quitting current AG: {}".format(res.text))

        return

    # 開啟交易通道
    def askTransaction(self, from_address, to_address, balance):
        print("[+] Sending transaction request to AG server")
        if self.agAddr == None:
            print("[!] AG not Found!")
            return
        print("\t[-] AG: [{}]".format(self.agAddr))
        data = self.beforeAction(from_address, to_address, balance)

        res = requests.post("{}/AG/askTransactions/".format(self.server), data=json.dumps(data))
        Jsystem = json.loads(requests.get("{}/AG/PublicKey/".format(self.server)).text)
        self.Public_AG = Point(Jsystem.get("Knx"), Jsystem.get("Kny"), curve=secp256k1)

        if "result" in dict(json.loads(res.text)).keys():
            print("[!] {}".format(json.loads(res.text)["result"]))
            return ""

        if "please try again" in res.text:
            print("[!] Recevier has not register AG")
            return ""

        # 這邊需要先轉錢給AG
        tx = {
            "chainId": 602602,
            "nonce": self.nonce,
            "to": self.agAddr,
            "value": int(balance),
            "gas": 200000,
            "gasPrice": self.w3.eth.gasPrice
        }

        signed_tx = self.w3.eth.account.sign_transaction(tx, getPrivateKey(self.w3))
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce += 1
        data["txnHash"] = str(tx_hash)
        ####################################################################################################

        txn = json.loads(res.text)["txn"]
        txnCH = json.loads(res.text)["txnCH"]
        contractAddr = json.loads(res.text)["contractAddr"]
        print("[+] Get Contract Txn:\n\t{}".format(txn))
        print("[+] Get Signature Txn:\n\t{}".format(txnCH))

        # contractAddr, txn, txnCH, txnData, pubX, pubY, status
        jsonObj = json.dumps({
            "contractTxn": txn,
            "SignatureTxn": txnCH,
            "ContractAddress": contractAddr,
            "AGAddress": self.agAddr,
            "SenderAddress": self.address,
            "Balance": balance,
        })

        if not "txns" in os.listdir('.'):
            os.mkdir("txns")

        with open("./txns/{}.json".format("Open-" + txn), "w") as file:
            file.write(jsonObj)

        # 要還原data
        data["from_address"] = self.address
        data["to_address"] = to_address
        data["balance"] = balance
        result = self.verifyTransactionHash(contractAddr, txn, txnCH, data, self.Public_AG.x, self.Public_AG.y, 0)
        print("[+] Verify Signature Txn: {}\n\t".format(result))
        return txnCH

    # 驗證交易通道的兩個Txn (from AG)
    def verifyTransactionHash(self, contractAddr, txn, txnCH, txnData, pubX, pubY, status):
        signature = self.w3.eth.getTransaction(txnCH)["input"]
        r = int(signature, 16)
        print("[+] Verify transaction signature:")
        result = self.part.VerifySignature(txn, r, pubX, pubY)

        if result == False:
            print("Verify Result: ", False)
            return False

        ## 判斷當下是 createTransaction 還是 payment
        if status == 0:
            status = "totalAmount"
        elif status == 1:
            status = "balance"
        contract = self.w3.eth.contract(abi=self.abi, address=contractAddr)

        contractInput = self.w3.eth.getTransaction(txn)["input"]
        func_obj, func_params = contract.decode_function_input(contractInput)

        # 比較合約參數是否一致
        ##print(func_params)
        if (func_params["_sender"] != txnData["from_address"] or func_params["_receiver"] != txnData[
            "to_address"] or
                func_params[status] != txnData["balance"]):
            print("\t[-] {} : {}".format(func_params["_sender"], txnData["from_address"]))
            print("\t[-] {} : {}".format(func_params["_receiver"], txnData["to_address"]))
            print("\t[-] {} : {}".format(func_params["totalAmount"], txnData["balance"]))
            print("[!] Transaction Data is wrong")
            return False
        else:
            print("\t[-] Verify: Pass")

        print("[+] Verify transaction msg:")
        msg = str(func_params["_sender"]) + str(func_params["_receiver"]) + str(func_params[status])

        result = None
        if status == "totalAmount":
            result = self.part.VerifySignature(msg, func_params["_signature"], self.Public_AG.x, self.Public_AG.y)
            print("Result: ", result)
            return result
        elif status == "balance":
            ## 因為payment是驗證別人的變色龍雜湊所以還需要索取CH
            print("Jelly fish")

        if result == False:
            print("Verify Transaction Args Verify Failed")
            return False

        return result

    # 接收芳於扣款時觸發 (手動輸入)
    def receivePayment(self, from_address, balance):

        if from_address in self.paymentRecord.keys():
            self.paymentRecord[from_address] += balance
        else:
            self.paymentRecord[from_address] = balance
        return

    # 付款方支付
    def payment(self, from_address, to_address, balance):
        print("[+] Sending payment request to AG server")
        data = self.beforeAction(from_address, to_address, balance)
        # data["from_address"] = from_address
        # data["to_address"] = to_address
        # data["balance"] = balance

        res = requests.post("{}/AG/payment/".format(self.server), data=json.dumps(data))
        Jsystem = json.loads(requests.get("{}/AG/PublicKey/".format(self.server)).text)
        self.Public_AG = Point(Jsystem.get("Knx"), Jsystem.get("Kny"), curve=secp256k1)

        if "result" in dict(json.loads(res.text)).keys():
            print("[!] {}".format(json.loads(res.text)["result"]))
            return ""

        if "please try again" in res.text:
            print("[!] Recevier has not register AG")
            return ""
        print("[+] Get Payment Txns")
        txn = json.loads(res.text)["txn"]
        txnCH = json.loads(res.text)["txnCH"]
        contractAddr = json.loads(res.text)["contractAddr"]
        paymentSign = json.loads(res.text)["paymentSign"]
        agAddress = json.loads(res.text)["Address"]

        print("\t[-] Get Payment Txn: {}".format(txn))
        print("\t[-] Get Signature Txn: {}".format(txnCH))
        print("\t[-] Contract Address: {}".format(contractAddr))
        print("\t[-] AG1's Address: {}".format(agAddress))
        print("\t[-] AG1's PublicKey:\n\t\tx: {}\n\t\ty: {}".format(
            hex(self.Public_AG.x), hex(self.Public_AG.y)))
        print("\t[-] Sender's Address: {}".format(self.address))
        print("\t[-] Payment Balance: {}".format(self.w3.fromWei(balance, 'ether')))
        print("\t[-] Get payment Signature: {}".format(paymentSign))

        jsonObj = json.dumps({
            "contractTxn": txn,
            "SignatureTxn": txnCH,
            "ContractAddress": contractAddr,
            "AGAddress": agAddress,
            "SenderAddress": self.address,
            "Balance": balance,
            "PaymentSign": paymentSign,
            "AGKnx": self.Public_AG.x,
            "AGKny": self.Public_AG.y
        })

        with open("./txns/{}.json".format("Pay-" + txn), "w") as file:
            file.write(jsonObj)

        # result = self.verifyTransactionHash(contractAddr, txn, txnCH, data, self.Public_AG.x, self.Public_AG.y, 1)

        # print("[+] Verify Signature Txn: {}\n\t".format(result))
        return res.text

    # 取得餘額
    def getBalance(self, from_address, to_address):
        data = json.dumps({
            "fromAddr": from_address,
            "toAddr": to_address
        })

        res = requests.post("{}/AG/getBalance/".format(self.server),
                            data=data)
        response = json.loads(res.text)
        return self.w3.fromWei(response.get("totalAmount"), 'ether'), \
               self.w3.fromWei(response.get("payedAmount"), 'ether')

    # 接收Txn後 要透過Txn領取金額
    def withdraw_from_Contract(self, txn, txnCH, contractAddr, senderAGAddr, data):
        print("[+] Withdrawing Phase ")
        # 取得發送方AG的公要
        senderAGPubX = int(data["AGKnx"])
        senderAGPubY = int(data["AGKny"])
        print("\t[-] AG PublicKey \n\t\tx: {}\n\t\ty: {}".format( hex(senderAGPubX), hex(senderAGPubY)))
        print("\t[-] payment Txn: ", txn)
        print("\t[-] signature Txn: ", txnCH)

        # 取得發送方與其AG的變色龍雜湊值
        res = requests.post("{}/AG/getChameleonHash/".format(self.server),
                            data=json.dumps({"clientAddr": data["from_address"], "agAddr": senderAGAddr}))
        HashX = int(json.loads(res.text)["HashX"])
        HashY = int(json.loads(res.text)["HashY"])
        print("\t[-] AG Hash: \n\t\tx: {}\n\t\ty: {}".format(hex(HashX), hex(HashY)))

        # 驗正簽章
        print("[+] Verifying payment Txn Phase")
        # 從txnCH上取得針對觸發payment函數的變色龍簽章(sender AG簽的)
        # AG把交易處發函數的txn簽呈變色龍 再發到區塊鏈
        txnSign = int(self.w3.eth.getTransaction(txnCH)["input"], 16) # 變色龍簽章
        msg = txn
        result = self.part.verifyPaymentSignature(msg, HashX, HashY, senderAGPubX, senderAGPubY, txnSign)
        print("\t[-] Get signature in signature Txn:\n\t\t", txnSign)
        print("\t[-] Txn Verify: ", result)
        if not result:
            return result

        # 比對合約參數
        print("[+] Comparing Arguments Phase")
        # 從txn 取得合約參數
        contract = self.w3.eth.contract(abi=self.abi, address=contractAddr)
        contractInput = self.w3.eth.getTransaction(txn)["input"]
        func_obj, func_params = contract.decode_function_input(contractInput)

        if func_params["_sender"] != data["from_address"] or func_params["_receiver"] != self.address or \
                func_params["balance"] != data["balance"]:
            print("[!]  Comparation Error!")
            print("\t[-] [Sender] {} : {}".format(func_params["_sender"], data["from_address"]))
            print("\t[-] [Receiver] {} : {}".format(func_params["_receiver"], self.address))
            print("\t[-] [Balance] {} : {}".format(func_params["balance"], data["balance"]))
            print("\t [-] Transaction Data is wrong")
            return False
        else:
            print("\t[-] Contract Args Verify: Pass")

        # 從智能合約中領錢
        try:
            txn = contract.functions.withdraw(self.w3.toChecksumAddress(data["from_address"]), self.address,
                                              int(data["paymentSign"], 16))
            txn.transact({
                "nonce": self.nonce,
                "from": self.address,
                'gasPrice': self.w3.eth.gasPrice,
            })
            self.nonce += 1
        except Exception as e:
            print("[!] {}".format(repr(e)))
        return result

    # 效能測試
    def PerformanceTesting(self, times, to_address, balance):
        cost = []
        for i in range(0, 1):
            self.askTransaction(self.address, to_address, int(balance))
            # if (i+1)%10 ==0:
            #   cost.append(time.time()-start)

        # print("----------------------------------------------------")
        # print("Transaction 耗時: {}".format(time.time() - start))
        # print("----------------------------------------------------")

        start = time.time()
        for i in range(0, times):
            self.payment(self.address, to_address, int(balance / times))
            if (i + 1) % 10 == 0:
                cost.append(time.time() - start)
        print("----------------------------------------------------")
        print("payment 耗時: ", str(cost))
        print("----------------------------------------------------")

    # 效能測試 - 一般交易
    def TransactionTesting(self, times, to_address, balance):
        start = time.time()
        print("[+] Now Testing Normal Transaction Performance")
        txn = {
            "from": self.address,
            'to': to_address,
            'value': int(balance / times),
            'gas': 2000000,
            'gasPrice': self.w3.eth.gasPrice,
            'nonce': self.w3.eth.getTransactionCount(self.address)
        }
        counter = 1
        for i in range(0, times):

            signed_tx = self.w3.eth.account.sign_transaction(txn, getPrivateKey(self.w3))
            tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            txn['nonce'] = self.w3.eth.getTransactionCount(self.address)
            if counter % 10 == 0:
                print("\t[-] {}: {}".format(counter, time.time() - start))
            counter += 1

        print("Normal Transaction 耗時: ", time.time() - start)
        print("----------------------------------------------")
        print("----------------------------------------------")

    # 效能測試 - 取款交易
    def withdrawTesting(self):
        jdata = []
        fileName = os.listdir('./txns')

        for fn in fileName:
            with open(os.path.join("./txns/", fn)) as file:
                jdata.append(json.loads(file.read()))
        balanceCounter = 0

        start = time.time()
        counter = 0
        cost = []
        for data in jdata:
            data["from_address"] = data["SenderAddress"]
            data["balance"] = data["Balance"]
            data["paymentSign"] = data["PaymentSign"]
            self.withdraw_from_Contract(
                data['contractTxn'], data['SignatureTxn'], data['ContractAddress'],
                data['AGAddress'], data
            )
            if (counter + 1) % 10 == 0:
                cost.append(time.time() - start)
            balanceCounter += data["balance"]
            counter += 1

        if self.w3.toWei(self.paymentRecord[data['from_address']], 'ether') != balanceCounter:
            print("[!] Local Balance Comparing is Error!")
            print("\t[!!] Please Contact the AG Node")
        print("time: ", str(cost))