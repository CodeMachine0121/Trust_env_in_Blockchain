from Crypto.PublicKey import ECC
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.Util.number import inverse


class Verifier:
    def __init__(self):
        self.eccKey = ECC.generate(curve='P-384')
        self.P = self.eccKey.pointQ
        self.ZP = int(self.P.__mul__(int(getrandbits(32))).x)  # 隨機找常數來相乘轉純量
        self.q = int(self.eccKey.d)

        ## 變色龍金鑰產生
        self.k = int(getrandbits(32))
        self.x = int(getrandbits(16))

        self.Y = self.x * self.ZP
        self.x_plum = pow(self.x, -1)

        ## key pair
        self.kn = int(getrandbits(16))
        self.Kn = self.kn * self.ZP

        ## 變色龍雜湊
        self.CHash = self.init_Hash()

    def init_Hash(self):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update("Helll".encode())
        Hm = int(H1.hexdigest(), 16)
        d = Hm * self.kn * self.x_plum
        r = (self.k - d) % self.q  # r for verifier
        return Hm * self.Kn + r * self.Y

    def Signing(self, msg):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        d = Hm * self.kn * self.x_plum
        r = (self.k - d) % self.q  # r for verifier

        return r

    def Verifying(self, msg, r_plum, Kn):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        CH = Hm * Kn + (r_plum * self.Y)
        return self.CHash == CH
