import requests
import json
from Lib.ChameleonShort.Participator import Participator
from Crypto.Random.random import getrandbits

server = "http://127.0.0.1:8000"


class Client:
    def __init__(self):
        res = requests.get('{}/AG/getSystem/'.format(server))
        Jsystem = json.loads(res.text)
        self.P = Jsystem.get("P")
        self.q = Jsystem.get("q")
        self.Kag = Jsystem.get("Kn")
        self.HK = Jsystem.get("HK")
        self.x_plum = Jsystem.get("x_plum")

    def RegisterAG(self):
        ## Session key Exchange
        ### 計算 zP
        z = int(getrandbits(16))
        zP = z * self.P
        res = requests.post('{}/AG/skExchange/'.format(server), data=json.dumps({'zP': zP}))
        kP = json.loads(res.text).get('Pk')
        ### 計算sk
        sk = kP * z
        print("[*] sk: ", sk)

        ### 建立變色龍物件
        CHclient = Participator(self.P, self.q, self.HK, self.x_plum, sk)

        ### 簽章
        msg = "Fuck"
        r = CHclient.Signing(msg)
        print("[*] r: ", r)
        print("[*] CH: ", CHclient.CHash)
        ### 送去審核
        res = requests.post("{}/AG/verifySign/".format(server), data=json.dumps({"msg": msg, "r": r, "Kn": CHclient.Kn}))

        return CHclient

client = Client()
CHclient = client.RegisterAG()
print()
