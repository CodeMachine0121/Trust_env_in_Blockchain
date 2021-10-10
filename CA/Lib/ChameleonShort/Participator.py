from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.PublicKey import ECC


class Participator:

    def __init__(self, Px, Py, q, HK):
        ## 變色龍金鑰產生
        self.P = ECC.EccPoint(Px, Py, 'P-384')
        self.q = q  # 一定要是質數
        self.Y = HK

        ## Session key 已經算好的
        self.z = -1
        self.sk = -1

        ## key pair
        self.kn = int(getrandbits(16))
        self.Kn = 0

        ## 轉純量的P
        self.ZP = -1
        ## 變色龍雜湊
        self.CHash = None

    ### 發送 key exchange 請求 收到另一半金鑰後再來計算session key ####
    def Session_key_Exchange(self, Ver_half_key):  ## sk = x^{-1}P * z
        self.z = int(getrandbits(16))
        self.sk = self.z * Ver_half_key
        Part_half_key = self.z * int(self.P.x)

        self.ZP = int(self.P.__mul__(self.sk).x)
        self.Kn = self.kn * self.ZP
        return Part_half_key

    def Signing(self, msg):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        d = Hm * self.kn
        r = (self.sk - d) % self.q  # r for client

        # 設定 變色龍雜湊
        self.CHash = Hm * self.Kn + r * self.ZP


        return r

    def Veriying(self, msg, r_plum, Kc):
        # K_c 對方的公鑰
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        Hm = int(H1.hexdigest(), 16)

        CH = Hm * Kc + r_plum * self.ZP
        return self.CHash == CH
