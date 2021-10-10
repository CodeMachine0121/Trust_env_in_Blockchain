from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits


class Participator:

    def __init__(self, P, q, HK, x_plum, sk):
        ## 變色龍金鑰產生
        self.P = P
        self.q = q
        self.Y = HK
        self.x_plum = x_plum

        ## key pair
        self.kn = int(getrandbits(16))
        self.Kn = self.kn * self.P

        ## Session key
        self.sk = sk

        ## 變色龍雜湊
        self.CHash = None

    def Signing(self, msg):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        d = Hm * self.kn * self.x_plum
        rc = (self.sk - d) % self.q  # r for client

        # 設定 變色龍雜湊
        self.CHash = Hm * self.Kn + rc * self.Y

        return rc

    def Veriying(self, msg, r_plum, Kc):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        CH = Hm * Kc + r_plum * self.Y
        return self.CHash == CH