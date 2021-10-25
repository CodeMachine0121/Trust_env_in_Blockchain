from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.PublicKey import ECC


class Participator:

    def __init__(self, Px, Py, q):
        self.P = ECC.EccPoint(Px, Py, curve='P-384')
        self.q = q

        ## Session key
        self.z = -1
        self.sk = -1

        ## key pair
        self.kn = int(getrandbits(32))
        self.Kn = self.P.__mul__(self.kn)

        ## 變色龍雜湊
        self.CHash =None

        ## 雜湊
        self.H1 = HMAC.new(b'', digestmod=SHA256)

    ### 發送 key exchange 請求 收到另一半金鑰後再來計算session key ####
    def Session_key_Exchange(self, Kx, Ky):  ## sk = x^{-1}P * z
        self.z = int(getrandbits(16))
        xp = ECC.EccPoint(Kx, Ky, curve='P-384')
        self.sk = int(xp.__mul__(self.z).x)
        # 初始化雜湊值
        self.CHash = self.init_Hash()
        # 要送回去的部分
        zp = self.P.__mul__(self.z)
        return int(zp.x), int(zp.y)

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

    def Verifying(self, msg, r_plum, KnX, KnY):
        if self.CHash is None:
            return 'Chameleon Hash is not initialized'

        self.H1.update(msg.encode())
        Hm = int(self.H1.hexdigest(), 16)

        Kn = ECC.EccPoint(KnX, KnY, curve='P-384')

        rp = self.P.__mul__(r_plum)
        CH = Kn.__mul__(Hm).__add__(rp)
        return self.CHash == CH
