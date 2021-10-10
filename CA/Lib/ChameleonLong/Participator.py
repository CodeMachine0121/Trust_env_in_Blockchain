from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.PublicKey import ECC


class Participator:

    def __init__(self, ZP, x_plum, k, q, HK, CHash):
        ## 變色龍金鑰產生
        #self.P = ECC.EccPoint(Px, Py, 'P-384')
        self.ZP = ZP  # 隨機找常數來相乘轉純量
        self.q = q  # 一定要是質數

        self.Y = HK
        self.k = k
        self.x_plum = x_plum

        ## key pair
        self.kn = int(getrandbits(16))
        self.Kn = self.kn * self.ZP

        ## 變色龍雜湊
        self.CHash = CHash

    def Signing(self, msg):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        d = Hm * self.kn * self.x_plum
        r = (self.k - d) % self.q  # r for client

        return r

    def Verifying(self, msg, r_plum, Kn):
        # K_n 對方的公鑰
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        CH = Hm * Kn + (r_plum * self.Y)
        return self.CHash == CH
