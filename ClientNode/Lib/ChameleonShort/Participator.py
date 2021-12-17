from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from ecc.curve import Point, secp256k1

class Participator:
    def __init__(self):
        self.P = secp256k1.G
        self.q = secp256k1.p

        # Key pair
        self.kn = int(getrandbits(64))
        self.Kn = self.P*self.kn

        self.sk = -1
        self.Chash = None

    def start_SessionKey(self, z, xpx, xpy, servPubX):
        xP = Point(xpx, xpy, curve=secp256k1)
        self.sk = int((xP*z).x)
        # 初始化 變色龍雜湊
        self.init_CHash(self.sk)
        
        return 

    def init_CHash(self, sk):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(b'Initialize')
        hm = int(H1.hexdigest(), 16)

        rP = (sk -( hm * self.kn))*self.P
        hKn = self.Kn*hm
        self.Chash = hKn+rP
    
        return 

    def VerifySignature(self, msg, r_plum, servPubX, servPubY):
        # 建立 ECC obj
        serv = Point(servPubX, servPubY, curve=secp256k1)
        # 建立 msg hash
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # Calculate
        hKn = serv*hm
        rP = self.P*r_plum
        chash = hKn+rP

        result = chash == self.Chash
        return result

    def MakeSignature(self, msg, servPubX):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)

        # calculate r
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)
        r = self.sk - (hm * self.kn)

        return r
