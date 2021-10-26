from Crypto.PublicKey import ECC
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.Util.number import inverse


class Verifier:
    def __init__(self, Px, Py, q, kn, k):
        self.P = ECC.EccPoint(Px, Py, curve='P-384')
        self.q = q

        ## 變色龍金鑰產生
        self.k = k
        self.x = int(getrandbits(2048))

        ## Session key
        self.x_plum = inverse(self.x, self.q)
        self.sk = -1  ## 還需要進行金鑰交換

        ## key pair
        self.kn = kn
        self.Kn = self.P.__mul__(self.kn)

        ## 變色龍雜湊
        self.CHash = None

        ## 雜湊
        self.H1 = HMAC.new(b'', digestmod=SHA256)

    ################################################
    #   server 需要先傳送自己的半金鑰，再接收另一半，再設定。     #
    ########################################################
    def Session_key_Exchange(self, ):  # sk = x^{-1} * z * P
        xp = self.P.__mul__(self.x_plum)
        return int(xp.x), int(xp.y)

    def set_Session_key(self, Kx, Ky):

        zp = ECC.EccPoint(Kx,Ky, curve='P-384')
        self.sk = int(zp.__mul__(self.x_plum).x) % self.q
        self.CHash = self.init_Hash()

    def init_Hash(self):
        if self.sk == -1:
            return 'Session key is not ready'

        self.H1.update('Hello'.encode())
        Hm = int(self.H1.hexdigest(), 16)
        d = (Hm * self.kn) % self.q
        r = (self.sk - d) % self.q

        rp = self.P.__mul__(r)
        CH = self.Kn.__mul__(Hm).__add__(rp)
        return CH

    def Signing(self, msg):
        if self.sk == -1:
            return 'Session key is not ready'

        self.H1.update(msg.encode())
        Hm = int(self.H1.hexdigest(), 16)
        d = (Hm * self.kn) % self.q
        r = (self.sk - d) % self.q
        return r

    def Verifying(self, msg, r_plum, KnX,KnY):
        if self.CHash is None:
            return 'Chameleon Hash is not initialized'
        Kn = ECC.EccPoint(KnX, KnY, curve='P-384')

        self.H1.update(msg.encode())
        Hm = int(self.H1.hexdigest(), 16)

        rp = self.P.__mul__(r_plum)
        CH = Kn.__mul__(Hm).__add__(rp)

        return self.CHash == CH
