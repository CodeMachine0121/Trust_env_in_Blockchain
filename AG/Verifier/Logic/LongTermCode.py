# -*- coding: utf-8 -*-
from .ChameleonLong.Participator import Participator as LPart
from .RSA.rsa import RSA_Library
import requests
import json


class LongTermCode:
    def __init__(self):
        self.CA_Addr = 'http://127.0.0.1:8000/'
        self.rsa = RSA_Library()

        self.Px, self.Py, self.k, self.q = self.get_CA_System()
        self.CA_pubKeys = None
        #self.lpart = LPart(self.Px, self.Py, self.k, self.q)
        #self.kn = self.lpart.kn
        

        pass

    def get_CA_System(self):
        # 向CA索取 System Parameters
        # Needs rsa cipher to decrypt the msg
        # Needs send own PublicKey to CA
        publicKey = self.rsa.publicKey.export_key().decode().replace('-----BEGIN PUBLIC KEY-----\n','').replace('\n-----END PUBLIC KEY-----','')

         
        res = requests.post(self.CA_Addr + 'Parameters/', data=json.dumps({'PublicKey':publicKey}))
        data = json.loads(res.text)
        

        # these are cipherText, need to be decrypted 
        Px = self.rsa.DecryptFunc( bytes.fromhex(data["Px"]))
        Py = self.rsa.DecryptFunc( bytes.fromhex(data["Py"]))
        k = self.rsa.DecryptFunc(  bytes.fromhex(data["k"]))
        q = self.rsa.DecryptFunc(  bytes.fromhex(data["q"]))
        
        

        #self.CA_pubKeys = (data["Knx"], data["Kny"])
        return Px, Py, k, q

    def makeSignature(self, msg):
        return self.lpart.Signing(msg)

    def verifySignature(self, signature, msg):
        return self.lpart.Verifying(msg, signature, self.CA_pubKeys[0], self.CA_pubKeys[1])
