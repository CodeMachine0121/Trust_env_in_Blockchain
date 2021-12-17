from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.PublicKey import ECC


class Participator:

    def __init__(self, Px, Py, k, q,):
        ## 變色龍金鑰產生
        self.P = ECC.EccPoint(Px, Py, 'P-384')
        self.q = q  # 一定要是質數
        self.k = k

        ## key pair
        self.kn = int(getrandbits(64))
        self.Kn = self.P.__mul__(self.kn)


        ## 變色龍雜湊
        self.CHash = self.init_Hash('This is Address')

    def init_Hash(self, msg):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16) % self.q
        r = (self.k - (hm*self.kn) % self.q) % self.q
        rP = self.P.__mul__(r)
        CH = self.Kn.__mul__(hm).__add__(rP)
        return int(CH.x), int(CH.y)

    def Signing(self, msg):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16) % self.q
        r = (self.k - (hm * self.kn) % self.q) % self.q
        return r

    def Verifying(self, msg, r_plum, Knx, Kny):
        Kn = ECC.EccPoint(Knx, Kny, 'P-384')
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16) % self.q
        rP = self.P.__mul__(r_plum)
        CH = Kn.__mul__(hm).__add__(rP)
        CH = (CH.x, CH.y)
        return self.CHash == CH

