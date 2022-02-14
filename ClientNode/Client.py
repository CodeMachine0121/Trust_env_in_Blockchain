import requests
import os
import json
from web3 import Web3
from Lib.ChameleonShort.Participator import Participator
from Crypto.Random.random import getrandbits
from Lib.RSA.rsa import RSA_Library
from ecc.curve import Point, secp256k1


def getAddress():
    w3 = Web3()
    for file in os.listdir("./Lib/Blockchain/keystore"):
        path = os.path.join('./Lib/Blockchain/keystore',file)

    with open(path) as f:
        priv = w3.eth.account.decrypt(f.read(), "mcuite")
    
    acct = w3.eth.account.privateKeyToAccount(priv)
    return acct.address

class Client:
    def __init__(self, server):
        self.server = server
        
        res = requests.get('{}/AG/Parameters/'.format(server))
        Jsystem = json.loads(res.text)
        
        self.Public_AG = Point(Jsystem.get("Knx"), Jsystem.get("Kny"), curve=secp256k1)
        
        self.part = Participator()
        
        self.address = getAddress() 


        #self.RegisterAG()
        self.rsa = RSA_Library()

        self.AG_RSA_PublicKey = Jsystem.get('RSA_PublicKey')
        
        self.contract = None
        


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

        ### 計算sk
        self.part.start_SessionKey(z, xpX, xpY, int(self.Public_AG.x))
        return 

    def beforeAction(self, msg):
        ### 簽章驗證
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
        
        return data

#########################################################

    def ask_for_Client_available(self, address):
        
       
        data = self.beforeAction(str(address))
        data["Target_address"] = address
            
        res = requests.post("{}/AG/clientAvailability/".format(self.server), data=json.dumps(data))

        print("[+] The result for the search: {}".format(res.text))
        
        return 
    
    def quit_current_AG(self): 
        data = self.beforeAction(str(self.address)+ str(self.part.sk))
        res = requests.post("{}/AG/quit_AG/".format(self.server), data=json.dumps(data))
        print("[+] Quitting current AG: {}".format(res.text))
        
        return 

    def askTransaction(self, from_address, to_address, balance):
        print("[+] Sending transaction request to AG server")
        data = self.beforeAction(str(from_address)+str(to_address)+str(balance))

        data["from_address"] = from_address
        data["to_address"] = to_address
        data["balance"] = balance

        res = requests.post("{}/AG/askTransactions/".format(self.server), data = json.dumps(data))
        print("[+] {}".format(res.text))

        return res.text
    
            


    def payment(self, from_address, to_address, balance):
        print("[+] Sending payment request to AG server")
        data = self.beforeAction(str(from_address)+str(to_address)+str(balance))
        data["from_address"] = from_address
        data["to_address"] = to_address
        data["balance"] = balance

        res = requests.post("{}/AG/payment/".format(self.server), data = json.dumps(data))
        print("[+] {}".format(res.text))
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
        data = self.beforeAction(str(from_address))
        data["from_address"] = from_address
        res = requests.post("{}/AG/setSenderAGContract/".format(self.server), data=json.dumps(data))
        
        fromAG = json.loads(res.text)["agAddress"]
        print("[+] Get fromAG: [{}]".format(fromAG)) 
        return fromAG


    def terminateTransaction(self, fromAG ,from_address, to_address):
        print("[+] Endding transaction contract...")
        print("\t[-] Getting TC's address: ")
        data = self.beforeAction(str(from_address)+str(to_address))
        data["fromAG"] = fromAG
        res = requests.post("{}/AG/getTContract/".format(self.server), json.dumps(data))
        tcAddr = json.loads(res.text)["tcAddress"]
        print("\t[-] Get TC: [{}]".format(tcAddr))

        # 讀取 server.json: 上面記錄用戶節點的URL
        with open("./Lib/Blockchain/server.json") as file:
            nodeServer = json.loads(file.read())["nodeServer"]
        with open("./Lib/Blockchain/TC.json") as file:
            abi = json.loads(file.read())["abi"]
        # 宣告合約物件
        w3 = Web3(Web3.HTTPProvider(nodeServer))
        tc = w3.eth.contract(abi=abi, address = tcAddr)

        # 從TC取得交易簽章並驗證
        signatures = tc.function.getSignatures(from_address, to_address).call()
        verifyResult = self.verifyTransactionSignature(signatures)


        # 計算簽章 (以往的簽章都會是AG的簽章 只有最後一筆的簽章是 receiver的)
        msg = str(from_address)+str(to_address)
        r = self.part.MakeSignature(msg)
       
        # 呼叫合約上的 terminateTransaction
        ### 接收方需要有自己的 Ethereum Console
        txn = tc.functions.terminateTransaction(from_address, to_address, r).transact({
                "nonce": w3.eth.getTransactionCount(w3.eth.coinbase),
                "from": w3.eth.coinbase
        })
        
        return 
    
    def verifyTransactionSignature(self,):
        # 用來驗證TC內的簽章
        
        return True
