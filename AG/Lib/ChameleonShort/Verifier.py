from Crypto.PublicKey import ECC
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.Util.number import inverse


class Verifier:
    def __init__(self):
        self.eccKey = ECC.generate(curve='P-384')
        self.P = self.eccKey.pointQ
        self.q = int(self.eccKey.d)

        ## 變色龍金鑰產生
        self.k = int(getrandbits(32))
        self.x = int(getrandbits(16))

        self.Y = int(self.P.__mul__(self.x).x)
        self.x_plum = inverse(self.x, self.q)


        ## Session key
        self.sk = -1  ## 還需要進行金鑰交換

        ## key pair
        self.kn = int(getrandbits(16))
        self.Kn = 0

        ## 轉純量的P
        self.ZP = -1
        ## 變色龍雜湊
        self.CHash = None


    ################################################
    #   server 需要先傳送自己的半金鑰，再接收另一半，再設定。     #
    ########################################################
    def Session_key_Exchange(self, ):  # sk = x^{-1} * z * P
        return self.x_plum * int(self.P.x)

    def set_Session_key(self, zP):
        self.sk = zP * self.x_plum
        self.ZP = int(self.P.__mul__(self.sk).x)
        self.Kn = self.kn * self.ZP


    def Signing(self, msg):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        d = Hm * self.kn
        r = (self.sk - d) % self.q  # r for verifier

        # 設定 變色龍雜湊
        self.CHash = Hm * self.Kn + r * self.ZP

        return r

    def Verifying(self, msg, r_plum, Kn):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        CH = Hm * Kn + r_plum * self.ZP

        return self.CHash == CH
