from ChameleonLong.Participator import Participator as LPart
import requests
import json


class LongTermCode:
    def __init__(self):
        self.CA_Addr = 'http://127.0.0.1:9999/'

        self.Px, self.Py, self.k, self.q = self.Get_System()
        self.CA_pubKeys = None
        self.lpart = LPart(self.Px, self.Py, self.k, self.q)
        self.kn = self.lpart.kn

        pass

    def Get_System(self):
        # 向CA索取 System Parameters
        res = requests.get(self.CA_Addr + 'Parameters/')
        data = json.loads(res.text)
        Px = data["Px"]
        Py = data["Py"]
        k = data["k"]
        q = data["q"]

        self.CA_pubKeys = (data["Knx"], data["Kny"])
        return Px, Py, k, q

    def makeSignature(self, msg):
        return self.lpart.Signing(msg)

    def verifySignature(self, signature, msg):
        return self.lpart.Verifying(msg, signature, self.CA_pubKeys[0], self.CA_pubKeys[1])
