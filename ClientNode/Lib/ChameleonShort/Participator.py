from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.PublicKey import ECC


class Participator:
    def __init__(self, Px, Py, q):
        self.P = ECC.EccPoint(Px, Py, curve='P-384')
        self.q = q

        # Key pair
        self.kn = int(getrandbits(64))
        self.Kn = self.P.__mul__(self.kn)

        # Session key,  變色龍雜湊: 考慮到往後的多AG功能 所以用MAP紀錄
        self.sessionKeys = dict()

    def start_SessionKey(self, z, xpx, xpy, servPubX):
        xP = ECC.EccPoint(xpx, xpy, curve='P-384')
        sk = int(xP.__mul__(z).x)
        # 初始化 變色龍雜湊
        Chash = self.init_CHash(sk)

        # 用公鑰x值紀錄
        self.sessionKeys[servPubX] = {
            "sk": sk,
            "Chash": Chash
        }
        return

    def init_CHash(self, sk):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(b'Initialize')
        hm = int(H1.hexdigest(), 16)

        rP = self.P.__mul__(sk - hm * self.kn)
        hKn = self.Kn.__mul__(hm)
        Chash = hKn.__add__(rP)
        return int(Chash.x), int(Chash.y)

    def VerifySignature(self, msg, r_plum, servPubX, servPubY):
        # 建立 ECC obj
        serv = ECC.EccPoint(servPubX, servPubY, curve='P-384')
        # 建立 msg hash
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # Calculate
        hKn = serv.__mul__(hm)
        rP = self.P.__mul__(r_plum)
        chash = hKn.__add__(rP)
        chash = (int(chash.x), int(chash.y))

        result = chash == self.sessionKeys[servPubX]['Chash']
        return result

    def MakeSignature(self, msg, servPubX):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)

        # calculate r
        sk = self.sessionKeys[servPubX]['sk']
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)
        r = sk - hm * self.kn

        # Calculate
        hKn = self.Kn.__mul__(hm)
        rP = self.P.__mul__(r)
        chash = hKn.__add__(rP)
        chash = (int(chash.x), int(chash.y))

        print("[Line 74] CH: ", chash[0])
        print("[Line 75] Kn: ", int(self.Kn.x))
        print("[Line 76] hKn: ", int(hKn.x))
        print("[Line 77] rp: ", int(rP.x))
        print("[Line 72] hm: ", hm)
        return r
