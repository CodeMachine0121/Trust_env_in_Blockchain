from Crypto.PublicKey import ECC
from Crypto.Hash import HMAC, SHA256
from Crypto.PublicKey import DSA
from Crypto.Random.random import getrandbits


class Verifier:
    def __init__(self):
        self.eccKey = ECC.generate(curve='P-384')
        self.P = int(self.eccKey.pointQ.x)
        self.q = int(self.eccKey.d)

        ## 變色龍金鑰產生
        self.k = int(getrandbits(32))
        self.x = int(getrandbits(16))

        self.Y = self.x * self.P
        self.x_plum = pow(self.x, -1)

        ## key pair
        self.kn = int(getrandbits(16))
        self.Kn = self.kn * self.P

        ## Session key
        self.sk = -1

        ## 變色龍雜湊
        self.CHash = None



    def Signing(self, msg):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        d = Hm * self.kn * self.x_plum
        rv = (self.sk - d) % self.q  # r for verifier

        # 設定 變色龍雜湊
        self.CHash = Hm * self.Kn + rv * self.Y

        return rv

    def Verifying(self, msg, r_plum, Kn):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        CH = Hm * Kn + r_plum * self.Y

        return self.CHash == CH
