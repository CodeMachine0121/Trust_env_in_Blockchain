from Crypto.PublicKey import ECC
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.Util.number import inverse


class Verifier:
    def __init__(self):
        self.ecc = ECC.generate(curve='P-384')
        self.P = self.ecc.pointQ
        self.Px = int(self.P.x)
        self.Py = int(self.P.y)
        self.q = int(self.ecc.d)

        self.k= int(getrandbits(2048))
        # 自己的 keypair
        self.kn = int(getrandbits(64))

        self.Kn = self.P.__mul__(self.kn)

        self.H1 = HMAC.new(b'', digestmod=SHA256)
        self.CHash = self.init_Hash('This is Address')

    def get_Kn(self):
        return int(self.Kn.x), int(self.Kn.y)

    def init_Hash(self,msg):
        self.H1.update(msg.encode())
        hm = int(self.H1.hexdigest(), 16)
        r = (self.k - (hm*self.kn)) % self.q
        rP = self.P.__mul__(r)
        CH = self.Kn.__mul__(hm).__add__(rP)
        return CH.x, CH.y

    def Signing(self, msg):
        self.H1.update(msg.encode())
        hm = int(self.H1.hexdigest(), 16)
        r = (self.k - (hm * self.kn)) % self.q
        return r

    def Verifying(self, msg, r_plum, Knx, Kny):
        Kn = ECC.EccPoint(Knx, Kny, 'P-384')

        self.H1.update(msg.encode())
        hm = int(self.H1.hexdigest(), 16)
        rP = self.P.__mul__(r_plum)
        CH = Kn.__mul__(hm).__add__(rP)
        CH = (CH.x, CH.y)
        return self.CHash == CH
