import requests
import json
import os
from .CipherAlgorithm.rsa import RSA_Library
from .ChameleonLong.Participator import Participator
from Crypto.Random.random import getrandbits


def setServer():
    with open("./Verifier/Logic/server.json") as file:
        server = json.loads(file.read())["CAHost"]
        return server


class longMiddleware:
    def __init__(self):
        # self.CA = 'http://140.125.32.10:8000'
        self.CA = setServer()
        print(self.CA)
        self.rsa = RSA_Library()

        data = json.dumps({"PublicKey": self.rsa.OutputPublic()})
        res = requests.post("{}/Parameters/".format(self.CA), data=data)

        dataBack = json.loads(res.text)
        self.CA_Knx = dataBack.get("Knx")
        self.CA_kny = dataBack.get("Kny")
        self.CA_k = dataBack.get("k")

        self.Participator = Participator(self.CA_k)

    def Register_to_CA(self):
        print("[+] Register to CA Phase: ")
        msg = hex(int(getrandbits(256)))
        r = self.Signature(msg=msg)
        data = {
            "msg": msg,
            'Knx': self.Participator.Kn.x,
            'Kny': self.Participator.Kn.y,
            "signature": r
        }
        # print(data)
        res = requests.post('{}/AG_Register/'.format(self.CA), data=json.dumps(data))
        print("[+] Register result: {}".format(res.text))
        return res.text

    def Signature(self, msg) -> int:
        return self.Participator.Signing(msg)

    def Verifing(self, msg, r_plum) -> bool:
        return self.Participator.Verifying(msg, r_plum, self.CA_Knx, self.CA_kny)
