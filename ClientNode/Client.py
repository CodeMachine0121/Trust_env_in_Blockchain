import requests
import json
from Lib.ChameleonShort.Participator import Participator
from Crypto.Random.random import getrandbits
from Crypto.PublicKey import ECC


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
#########################################################


        ### 簽章
        msg = "Back"
        r = self.part.MakeSignature(msg, int(self.Public_AG.x))
        ### 送去審核
        res = requests.post("{}/AG/shortReceive/".format(self.server),
                            data=json.dumps({"msg": msg,
                                             "r": r,
                                             "Knx": int(self.part.Kn.x),
                                             "Kny": int(self.part.Kn.y),
                                             }))
        response = json.loads(res.text)
        result = self.part.VerifySignature(response.get('msg'), response.get('signature'), int(self.Public_AG.x), int(self.Public_AG.y))
        print("[*] Result: ", result)

        return res.text



client = Client('http://127.0.0.1:8000')
print()
