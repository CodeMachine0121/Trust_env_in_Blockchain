import requests
import json
import os
from .RSA.rsa import RSA_Library
from .ChameleonLong.Participator import Participator

class longMiddleware:
    def __init__(self):
        self.CA = 'http://140.125.32.10:8000'
        self.rsa = RSA_Library()

        data = json.dumps({"PublicKey": self.rsa.OutputPublic()})
        res = requests.post("{}/Parameters/".format(self.CA), data = data)

        dataBack = json.loads(res.text)
        self.CA_Knx = dataBack.get("Knx")
        self.CA_kny = dataBack.get("Kny")
        self.CA_k = dataBack.get("k")

        self.Participator = Participator(self.CA_k)

        self.Register_to_CA()
        return

    def Register_to_CA(self):
        print("[+] Register to CA")
        r = self.Signature(msg='m')
        data = {
            "msg": 'm',
            'Knx': self.Participator.Kn.x,
            'Kny': self.Participator.Kn.y,
            "signature": r
        }
        #print(data)
        res = requests.post('{}/AG_Register/'.format(self.CA), data=json.dumps(data))
        print("[+] Register result: {}".format(res.text))
        return res.text

    def Signature(self, msg) -> int:
        return self.Participator.Signing(msg)

    def Verifing(self, msg, r_plum) -> bool:
        return self.Participator.Verifying(msg, r_plum, self.CA_Knx, self.CA_kny)
