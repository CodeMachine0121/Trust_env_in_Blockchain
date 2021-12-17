import requests
import json
from Lib.ChameleonShort.Participator import Participator
from Crypto.Random.random import getrandbits
from Lib.RSA.rsa import RSA_Library
from ecc.curve import Point, secp256k1

class Client:
    def __init__(self, server):
        self.server = server
        
        res = requests.get('{}/AG/Parameters/'.format(server))
        Jsystem = json.loads(res.text)
        
        self.Public_AG = Point(Jsystem.get("Knx"), Jsystem.get("Kny"), curve=secp256k1)
        
        self.part = Participator()
        
        self.chainAddress = "will be down with web3"


        self.RegisterAG()
        self.rsa = RSA_Library()

        self.AG_RSA_PublicKey = Jsystem.get('RSA_PublicKey')

        self.chainAddress = "will be down with web3"

    ## 更換server
    def Refresh_AG(self, server):
        self.__init__(server)

    ## 設定 Session Key
    def RegisterAG(self):
        ## Session key Exchange
        ### 計算 zP
        z = int(getrandbits(128))
        zpX = (self.part.P*z).x
        zpY = (self.part.P*z).y

        res = requests.post('{}/AG/SessionKey/'.format(self.server),
                            data=json.dumps({
                                'zpX': zpX,
                                'zpY': zpY,
                                'KnX': int(self.part.Kn.x),
                                'address': self.chainAddress
                            }))

        xpX = json.loads(res.text).get('xPX')
        xpY = json.loads(res.text).get('xPY')

        ### 計算sk
        self.part.start_SessionKey(z, xpX, xpY, int(self.Public_AG.x))
        return 
#########################################################

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
                "chainAddress": self.chainAddress,
            }
        
        return data

#########################################################

    def ask_for_Client_available(self, address):
        
       
        data = self.beforeAction()
        data["Target_address"] = address
            
        res = requests.post("{}/AG/clientAvailability/".format(self.server), data=json.dumps(data))

        print("[+]The result for the search: {}".format(res.text))
        
        return 
    
    def quit_current_AG(self):
        data = self.beforeAction()
        res = requests.post("{}/AG/quit_AG/".format(self.server), data=json.dumps(data))
        print("[+] Quitting current AG: {}".format(res.text))
        
        return 

client = Client('http://127.0.0.1:9999')
client.ask_for_Client_available(client.chainAddress)
client.quit_current_AG()
print()
