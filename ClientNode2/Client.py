import requests
import os
import json
from web3 import Web3
#from web3.middleware import geth_poa_middleware
from Lib.ChameleonShort.Participator import Participator
from Crypto.Random.random import getrandbits
from Lib.RSA.rsa import RSA_Library
from ecc.curve import Point, secp256k1
import time
from progress.bar import Bar

def getPrivateKey(web3):

    keyfile = os.listdir("./Lib/Blockchain/keystore")[0]
    with open(os.path.join("./Lib/Blockchain/keystore", keyfile)) as file:
        encrypted_key = file.read()
        privateKey = web3.eth.account.decrypt(encrypted_key,"mcuite")        
    return privateKey


def getServerAddress():
    # 讀取 server.json: 上面記錄用戶節點的URL
    with open("./Lib/Blockchain/server.json") as file:
        nodeServer = json.loads(file.read())["nodeServer"]
    return nodeServer


def getAddress():
    w3 = Web3()
    for file in os.listdir("./Lib/Blockchain/keystore"):
        path = os.path.join('./Lib/Blockchain/keystore',file)

    with open(path) as f:
        priv = w3.eth.account.decrypt(f.read(), "mcuite")
    
    acct = w3.eth.account.privateKeyToAccount(priv)

    return w3.toChecksumAddress(acct.address)

class Client:
    def __init__(self, server):
        self.server = server
        
        res = requests.get('{}/AG/Parameters/'.format(server))
        Jsystem = json.loads(res.text)
        
        self.Public_AG = Point(Jsystem.get("Knx"), Jsystem.get("Kny"), curve=secp256k1)
        print("AG: Public Key X: ", self.Public_AG.x)
        print("AG: Public Key Y: ", self.Public_AG.y)


        self.part = Participator()
         


        #self.RegisterAG()
        self.rsa = RSA_Library()

        self.AG_RSA_PublicKey = Jsystem.get('RSA_PublicKey')
        self.agAddr = None
        self.contract = None
        self.nodeServer = getServerAddress()

        self.w3 = Web3(Web3.HTTPProvider(self.nodeServer))
        #self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        

        self.abi = self.getABI()
        self.address = getAddress()
        self.nonce = self.w3.eth.getTransactionCount(self.address)
        print("Public Key X: ", self.part.Kn.x)
        print("Public Key Y: ", self.part.Kn.y)

    ## 讀取ABI
    def getABI(self,):
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
    def RegisterAG(self):
    ##Session key Exchange
        ### 計算 zP
        z = int(getrandbits(128))
        zpX = (self.part.P*z).x
        zpY = (self.part.P*z).y

        res = requests.post('{}/AG/SessionKey/'.format(self.server),
                            data=json.dumps({
                                'zpX': zpX,
                                'zpY': zpY,
                                'KnX': int(self.part.Kn.x),
                                'address': self.address
                            }))

        xpX = json.loads(res.text).get('xPX')
        xpY = json.loads(res.text).get('xPY')

        self.agAddr = json.loads(res.text).get("address")

        ### 計算sk
        self.part.start_SessionKey(z, xpX, xpY, int(self.Public_AG.x))
        return 

    def beforeAction(self, from_address, to_address, balance):
        ### 簽章驗證
        msg = str(from_address)+str(to_address)+str(balance)
        en_msg = self.rsa.EncryptFunc(msg, self.AG_RSA_PublicKey)
        en_from_address = self.rsa.EncryptFunc(str(from_address), self.AG_RSA_PublicKey)
        en_to_address = self.rsa.EncryptFunc(str(to_address), self.AG_RSA_PublicKey)
        en_balance = self.rsa.EncryptFunc(str(balance), self.AG_RSA_PublicKey)
        r = self.part.MakeSignature(msg)
        publicKey = self.rsa.OutputPublic()
        #print("[Debug]: {}".format(en_msg))
        data = {
                "from_address":en_from_address,
                "to_address":en_to_address,
                "balance":en_balance,
                "msg": en_msg,
                "r": r,
                "Knx": int(self.part.Kn.x),
                "Kny": int(self.part.Kn.y),
                "RSA_publicKey": publicKey,
                "chainAddress": self.address,
            }
        
        return data

#########################################################

    def ask_for_Client_available(self, address):
        
       
        data = self.beforeAction(str(address))
        data["Target_address"] = address
            
        res = requests.post("{}/AG/clientAvailability/".format(self.server), data=json.dumps(data))

        print("[+] The result for the search: {}".format(res.text))
        
        return 
    
    def quit_current_AG(self): 
        msg = str(self.address)+str(self.part.sk)
        en_msg = self.rsa.EncryptFunc(msg, self.AG_RSA_PublicKey)
        
        r = self.part.MakeSignature(msg)
        publicKey = self.rsa.OutputPublic()
        #print("[Debug]: {}".format(en_msg))
        data = {
                "msg": en_msg,
                "r": r,
                "Knx": int(self.part.Kn.x),
                "Kny": int(self.part.Kn.y),
                "RSA_publicKey": publicKey,
                "chainAddress": self.address,
            }

        #data = self.beforeAction(str(self.address)+ str(self.part.sk))
        res = requests.post("{}/AG/quit_AG/".format(self.server), data=json.dumps(data))
        print("[+] Quitting current AG: {}".format(res.text))
        
        return 

    def askTransaction(self, from_address, to_address, balance):
        print("[+] Sending transaction request to AG server")
        if self.agAddr == None:
            print("[!] AG not Found!")
            return 
        print("\t[-] AG: [{}]".format(self.agAddr))
        data = self.beforeAction(from_address, to_address, balance)
        #data = self.beforeAction(str(from_address)+str(to_address)+str(balance))
        #data["from_address"] = from_address
        #data["to_address"] = to_address
        #data["balance"] = balance
        
        # 這邊需要先轉錢給AG
        tx = {
            "chainId": 602602,
            "nonce": self.nonce,
            "to":self.agAddr,
            "value": int(balance),
            "gas": 200000,
            "gasPrice": self.w3.eth.gasPrice
        }

        signed_tx = self.w3.eth.account.sign_transaction(tx, getPrivateKey(self.w3))
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.nonce+=1

        data["txnHash"] = str(tx_hash)

        res = requests.post("{}/AG/askTransactions/".format(self.server), data = json.dumps(data))
        
        txn = json.loads(res.text)["txn"]
        txnCH = json.loads(res.text)["txnCH"]
        contractAddr = json.loads(res.text)["contractAddr"]
        print("[+] Get Contract Txn:\n\t{}".format(txn))
        print("[+] Get Signature Txn:\n\t{}".format(txnCH))
        
        # contractAddr, txn, txnCH, txnData, pubX, pubY, status
        jsonObj = json.dumps({
            "contractTxn":txn, 
            "SignatureTxn": txnCH, 
            "ContractAddress": contractAddr,
            "AGAddress":self.agAddr,
            "SenderAddress":self.address,
            "Balance":balance,
        })
        
        with open("./txns/{}.json".format("Open-"+txn), "w") as file:
            file.write(jsonObj)

        ## 要還原data
        data["from_address"] = self.address
        data["to_address"] = to_address
        data["balance"] = balance
        result = self.verifyTransactionHash(contractAddr, txn, txnCH, data, self.Public_AG.x, self.Public_AG.y, 0)
        print("[+] Verify Signature Txn: {}\n\t".format(result))
        return txnCH
    

    def payment(self, from_address, to_address, balance):
        print("[+] Sending payment request to AG server")
        data = self.beforeAction(from_address, to_address, balance)
        #data["from_address"] = from_address
        #data["to_address"] = to_address
        #data["balance"] = balance

        res = requests.post("{}/AG/payment/".format(self.server), data = json.dumps(data))
        txn = json.loads(res.text)["txn"]
        txnCH = json.loads(res.text)["txnCH"]
        contractAddr = json.loads(res.text)["contractAddr"]
        paymentSign = json.loads(res.text)["paymentSign"]
        agAddress = json.loads(res.text)["Address"]

        print("[+] Get Contract Txn:\n\t{}".format(txn))
        print("[+] Get Signature Txn: \n\t{}".format(txnCH))
        print("[+] Contract Address: \n\t{}".format(contractAddr))
        print("[+] AG's Address:\n\t{}".format(agAddress))
        print("[+] Sender's Address:\n\t{}".format(self.address))
        print("[+] Payment Balance: \n\t{}".format(balance))
        print("[+] Get payment Signature: \n\t{}".format(paymentSign))
        
        jsonObj = json.dumps({
            "contractTxn":txn, 
            "SignatureTxn": txnCH, 
            "ContractAddress": contractAddr,
            "AGAddress":agAddress,
            "SenderAddress":self.address,
            "Balance":balance,
            "PaymentSign":paymentSign})
        
        with open("./txns/{}.json".format("Pay-"+txn), "w") as file:
            file.write(jsonObj)

        #result = self.verifyTransactionHash(contractAddr, txn, txnCH, data, self.Public_AG.x, self.Public_AG.y, 1)

        #print("[+] Verify Signature Txn: {}\n\t".format(result))
        return res.text

    def getContractBalance(self, from_address, to_address):
        print("[+] Getting Balance information:")
        data = self.beforeAction(str(from_address)+str(to_address))    
        data["fromAddr"] = from_address
        data["toAddr"] = to_address


        res = requests.post("{}/AG/getContractBalance/".format(self.server),data=json.dumps(data))
        res = json.loads(res.text)

        contractAmount = res["contractAmount"] 
        agAmount = res["agAmount"]
        
        print("\t[+] on Contract")
        print("\t\t[-] Total Amount: {}".format(contractAmount[0]))
        print("\t\t[-] Current Amount: {}".format(contractAmount[1]))
        print("\t[+] on AG")
        print("\t\t[-]Total Amount: {}".format(agAmount[0]))
        print("\t\t[-]Current Amount: {}".format(agAmount[1]))

        return
    
    # 向AG設置發送方的TC位址
    def setTransactionContract(self, from_address):
        print("[+] Setting transaction contract...")
        msg = str(from_address)
        en_msg = self.rsa.EncryptFunc(msg, self.AG_RSA_PublicKey)
        r = self.part.MakeSignature(msg)
        publicKey = self.rsa.OutputPublic()
        #print("[Debug]: {}".format(en_msg))
        data = {
                "msg": en_msg,
                "r": r,
                "Knx": int(self.part.Kn.x),
                "Kny": int(self.part.Kn.y),
                "RSA_publicKey": publicKey,
                "chainAddress": self.address,
                "from_address": from_address
            }
        res = requests.post("{}/AG/setSenderAGContract/".format(self.server), data=json.dumps(data))
        
        fromAG = json.loads(res.text)["agAddress"]
        print("[+] Get fromAG: [{}]".format(fromAG)) 
        return fromAG






    def verifyTransactionSignature(self, fromAG, fromAddr, toAddr, signatures, txnHistory):
        # 用來驗證TC內的簽章
        ## 需要先取得fromAG的公鑰 Knx, Kny，變色龍 (從RC取得) -> 向AG請求
        print("[+] Getting Public Key of sender AG")
        res = requests.post("{}/AG/getPublicKey/".format(self.server), data=json.dumps({
            "agAddress": fromAG
            }))
        data = json.loads(res.text)
        Knx = data["x"]
        Kny = data["y"]
        #print("\t[-] x: ", Knx)
        #print("\t[-] y: ", Kny)

        print("\t[-] Now Verifying Signatures")
        #print("\t\t[-] signatures: \n\t{}".format(signatures))
        print("\t[-] Getting Chameleon Hash of sender: [{}]".format(fromAddr))
        
        res = requests.post("{}/AG/getChameleonHash/".format(self.server),data=json.dumps({"clientAddr": fromAddr,"agAddr":fromAG}))
        
        CHashX = json.loads(res.text)["HashX"]
        CHashY = json.loads(res.text)["HashY"]
        #print("\t\t({},{})".format(CHashX, CHashY))
        # 執行驗證程序 相關code寫在 SPart內
        ## 編排驗證訊息
        msgs = list()
        for index in txnHistory.keys():
            if index != "0":
                msgs.append(str(fromAddr)+str(toAddr)+str(txnHistory[index]["currentAmount"]))
            else:
                msgs.append(str(fromAddr)+str(toAddr)+str(txnHistory["0"]["totalAmount"]))

        # 驗證訊息簽章
        verifyResult = self.part.verifyTransactionSignature(msgs, CHashX, CHashY,Knx,Kny,signatures)
        
        return verifyResult

    # 驗證交易雜湊值 (from AG)
    def verifyTransactionHash(self, contractAddr, txn, txnCH, txnData, pubX, pubY, status):
    
        signature = self.w3.eth.getTransaction(txnCH)["input"]
        r = int(signature, 16)
        result = self.part.VerifySignature(txn, r, pubX, pubY)
        
        if result == False:
            print("Verify Result: ", False)
            return False

        ## 判斷當下是 createTransaction 還是 payment
        if status == 0:
            status = "totalAmount"
        elif status ==1 :
            status = "balance"
        contract = self.w3.eth.contract(abi=self.abi, address=contractAddr)
        
        contractInput = self.w3.eth.getTransaction(txn)["input"]
        func_obj, func_params = contract.decode_function_input(contractInput)
        
        # 比較合約參數是否一致
        ##print(func_params)
        if( func_params["_sender"] != txnData["from_address"] or func_params["_receiver"] != txnData["to_address"] or func_params[status] != txnData["balance"]):
            print("\t[-] {} : {}".format(func_params["_sender"] , txnData["from_address"]))
            print("\t[-] {} : {}".format(func_params["_receiver"] , txnData["to_address"]))
            print("\t[-] {} : {}".format(func_params["totalAmount"] , txnData["balance"]))
            print("[!] Transaction Data is wrong")
            return False
        else:
            print("\t[-] Verify: Pass")
        msg = str(func_params["_sender"]) + str(func_params["_receiver"]) + str(func_params[status])
        
        result = None
        if status == "totalAmount":
            result = self.part.VerifySignature(msg, func_params["_signature"], self.Public_AG.x, self.Public_AG.y)
            print("Result: ", result)
            return result
        elif status == "balance" :
            ## 因為payment是驗證別人的變色龍雜湊所以還需要索取CH
            print("Jelly fish")

        if result == False:
            print("Verify Transaction Args Verify Failed")
            return False
        
        return result
       
    
    # 接收TXn後 要透過Txn領取金額
    def withdraw_from_Contract(self, txn, txnCH, contractAddr, senderAGAddr, data):
        print("[+] Withdrawing the Eth")
        ## via QR Code
        contract = self.w3.eth.contract(abi=self.abi, address=contractAddr)
        
        ## 取得發送方AG的公要
        res = requests.post("{}/AG/getPublicKey/".format(self.server), data = json.dumps({"agAddress": senderAGAddr}))
        senderAGPubX = int(json.loads(res.text)["x"])
        senderAGPubY = int(json.loads(res.text)["y"])
        print("\t[-] sender AG PublicKey X: ", senderAGPubX)
        print("\t[-] sedner AG PublicKey Y: ", senderAGPubY)
        
        ## 取得發送方與其AG的變色龍雜湊值
        res = requests.post("{}/AG/getChameleonHash/".format(self.server), data=json.dumps({"clientAddr": data["from_address"], "agAddr":senderAGAddr}))
        HashX = int(json.loads(res.text)["HashX"])
        HashY = int(json.loads(res.text)["HashY"])
        print("\t[-] AG Hash: \n\t\tx: {}\n\t\ty: {}".format(HashX, HashY))
       
        ## 從txnCH上取得變色龍簽章
        txnSign = int(self.w3.eth.getTransaction(txnCH)["input"],16)
        
        ## 從txn 取得合約參數
        contract = self.w3.eth.contract(abi=self.abi, address=contractAddr)
        contractInput = self.w3.eth.getTransaction(txn)["input"]
        func_obj, func_params = contract.decode_function_input(contractInput)
        
        if func_params["_sender"] != data["from_address"] or func_params["_receiver"] != self.address or func_params["balance"] != data["balance"]:
            print("[!]  Comparation Error!")
            print("\t[-] [Sender] {} : {}".format(func_params["_sender"] , data["from_address"]))
            print("\t[-] [Receiver] {} : {}".format(func_params["_receiver"] , self.address))
            print("\t[-] [Balance] {} : {}".format(func_params["balance"] , data["balance"]))
            print("\t [-] Transaction Data is wrong")
            return False
        else:
            print("\t[-] Contract Args Verify: Pass")
        
        ## 驗正簽章
        msg =  txn       
        result = self.part.verifyPaymentSignature(msg, HashX, HashY, senderAGPubX, senderAGPubY, txnSign)
        print("\t[-] Txn Verify: ",result)
        
        if result == False:
            return result

        ## 從智能合約中領錢
        
        ### 要取得AG對於該筆payment的交易簽章
        a1,a2 = contract.functions.test(data["from_address"], self.address).call()
        print("[Debug]: ", a1, "\n[Debug]: ", a2)
        print("[Debug]: ", self.w3.eth.coinbase)
        
        
        txn = contract.functions.withdraw(self.w3.toChecksumAddress(data["from_address"]), self.address, int(data["paymentSign"],16)).transact({
                "nonce": self.nonce,
                "from": self.address,
                'gasPrice': self.w3.eth.gasPrice,
        })
        self.nonce+=1 
        
        return result
    

    ## 效能測試
    def PerformanceTesting(self, times, to_address, balance):
        start = time.time()
        cost=[]
        for i in range(0,1):
            self.askTransaction(self.address, to_address, int(balance))
            #if (i+1)%10 ==0:
            #   cost.append(time.time()-start)


        print("----------------------------------------------------")
        print("Transaction 耗時: {}".format(time.time()-start))
        print("----------------------------------------------------")

        for i in range(0,times):
            self.payment(self.address, to_address, int(balance/times))
            if (i+1)%10 ==0:
                cost.append(time.time()-start)
        
        for counter in range(0,len(cost)):
            print("\t[-] {}: {}".format((counter+1)*10, cost[counter]))
            


        #print("----------------------------------------------------")
        #print("payment 耗時: {}".format(time.time()-start))
        #print("----------------------------------------------------")
    
    ## 效能測試 - 一般交易
    def TransactionTesting(self, times, to_address, balance):
        start = time.time()
        print("[+] Now Testing Normal Transaction Performance")
        txn = {
            "from": self.address,
            'to':to_address,
            'value': int(balance/times),
            'gas': 2000000,
            'gasPrice': self.w3.eth.gasPrice,
            'nonce':self.w3.eth.getTransactionCount(self.address)
        }
        counter=1
        bar = Bar('Processing',max = times)
        for i in range(0,times):

            signed_tx = self.w3.eth.account.sign_transaction(txn, getPrivateKey(self.w3))
            tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            txn['nonce']=self.w3.eth.getTransactionCount(self.address)
            if counter % 10 == 0 :
                print("\t[-] {}: {}".format(counter, time.time()-start))
            counter+=1

        print("Normal Transaction 耗時: ", time.time()-start)
        print("----------------------------------------------")
        print("----------------------------------------------")



    def withdrawTesting(self):
        jdata = []
        fileName = os.listdir('./txns')
        
        for fn in fileName:
            with open(os.path.join("./txns/", fn)) as file:
                jdata.append(json.loads(file.read()))
         
        counter=1
        cost=[]
        start = time.time()
        
        for data in jdata:
            data["from_address"] = data["SenderAddress"]
            data["balance"] = data["Balance"]
            data["paymentSign"]=data["PaymentSign"]
            self.withdraw_from_Contract(
                    data['contractTxn'], data['SignatureTxn'],data['ContractAddress'], 
                    data['AGAddress'], data
            )
            if counter%10==0:
                cost.append(time.time()-start)
            counter+=1
        counter =10
        for t in cost:
            print("\t[-] {}: {}".format(counter, t))
            counter+=10



