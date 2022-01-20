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


#        self.RegisterAG()
        self.rsa = RSA_Library()

        self.AG_RSA_PublicKey = Jsystem.get('RSA_PublicKey')




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

    def beforeAction(self ):
        ### 簽章驗證
        msg = "Back"
        en_msg = self.rsa.EncryptFunc(msg, self.AG_RSA_PublicKey)
        r = self.part.MakeSignature(msg, int(self.Public_AG.x))
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
        
       
        data = self.beforeAction()
        data["Target_address"] = address
            
        res = requests.post("{}/AG/clientAvailability/".format(self.server), data=json.dumps(data))

        print("[+] The result for the search: {}".format(res.text))
        
        return 
    
    def quit_current_AG(self):
        data = self.beforeAction()
        res = requests.post("{}/AG/quit_AG/".format(self.server), data=json.dumps(data))
        print("[+] Quitting current AG: {}".format(res.text))
        
        return 

    def askTransaction(self, from_address, to_address, balance):
        print("[+] Sending transaction request to AG server")
        data = self.beforeAction()
        data["from_address"] = from_address
        data["to_address"] = to_address
        data["balance"] = balance

        res = requests.post("{}/AG/askTransactions/".format(self.server), data = json.dumps(data))
        


client = Client('http://140.125.32.10:8888')

#client.ask_for_Client_available(client.address)
client.RegisterAG()
#client.askTransaction(client.address, client.address ,10)

#client.quit_current_AG()
#client.ask_for_Client_available(client.address)
print()
