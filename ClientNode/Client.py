import requests
import json
from Lib.ChameleonShort.Participator import Participator
from Crypto.Random.random import getrandbits
from Crypto.PublicKey import ECC
from Lib.RSA.rsa import RSA_Library

class Client:
    def __init__(self, server):
        self.server = server
        res = requests.get('{}/AG/Parameters/'.format(server))
        Jsystem = json.loads(res.text)
        self.Public_AG = ECC.EccPoint(Jsystem.get("Knx"), Jsystem.get("Kny"), curve='P-384')
        self.part = Participator(Jsystem.get('Px'), Jsystem.get('Py'), Jsystem.get('q'))

        self.RegisterAG()

    ## 更換server
    def Refresh_AG(self, server):
        self.__init__(server)

    ## 設定 Session Key
    def RegisterAG(self):
        ## Session key Exchange
        ### 計算 zP
        z = int(getrandbits(128))
        zpX = int(self.part.P.__mul__(z).x)
        zpY = int(self.part.P.__mul__(z).y)

        res = requests.post('{}/AG/SessionKey/'.format(self.server),
                            data=json.dumps({
                                'zpX': zpX,
                                'zpY': zpY,
                                'KnX': int(self.part.Kn.x)
                            }))

        xpX = json.loads(res.text).get('xPX')
        xpY = json.loads(res.text).get('xPY')

        ### 計算sk
        self.part.start_SessionKey(z, xpX, xpY, int(self.Public_AG.x))
        return 
#########################################################

    def makeAction(commandMsg):
        ### 簽章
        commandMsg = "Back"
        en_commandMsg = rsa.EncryptFunc(commandMsg) 
        r = self.part.MakeSignature(msg, int(self.Public_AG.x))
        publicKey = self.rsa.publicKey.export_key().decode().replace('-----BEGIN PUBLIC KEY-----\n','').replace('\n-----END PUBLIC KEY-----','')


        ### 送去審核
        res = requests.post("{}/AG/shortReceive/".format(self.server),
                            data=json.dumps({"msg": en_commandMsg,
                                             "r": r,
                                             "Knx": int(self.part.Kn.x),
                                             "Kny": int(self.part.Kn.y),
                                             "publicKey": publicKey
                                             }))
        response = json.loads(res.text)
        AG_public = response.get('publicKey')
        decrypt_resultMsg =rsa.DecryptFunc(response.get('msg'), AG_public)

        result = self.part.VerifySignature(decrypt_resultMsg, response.get('signature'), int(self.Public_AG.x), int(self.Public_AG.y))
        print("[*] Result: ", result)

        return res.text

    # 要執行的動作
    def makeActions(action_msg):
        pass

client = Client('http://127.0.0.1:9999')
print()
