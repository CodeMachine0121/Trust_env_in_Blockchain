from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.PublicKey import ECC


class Verifier:
    def __init__(self):
        self.ecc = ECC.generate(curve='P-384')
        self.P = self.ecc.pointQ
        self.q = int(self.ecc.d)

        # Trap door key
        self.x = int(getrandbits(32))
        # Key pair
        self.kn = int(getrandbits(64))
        self.Kn = self.P.__mul__(self.kn)

        # Session key,  變色龍雜湊: 因為要記錄多個使用者所以用MAP紀錄
        self.sessionKeys = dict()

    def start_SessionKey(self):
        xP = self.P.__mul__(self.x)
        return int(xP.x), int(xP.y)

    def set_SessionKey(self, zpx, zpy, cli_PubX):
        zP = ECC.EccPoint(zpx, zpy, curve='P-384')
        sk = int(zP.__mul__(self.x).x)

        # 初始化 變色龍雜湊值
        Chash = self.init_CHash(sk)
        print("[Line 34] CH: ", Chash[0])
        print("[Line 35] SK: ", sk)
        # 用公鑰x值紀錄
        self.sessionKeys[cli_PubX] = {
            "sk": sk,
            "Chash": Chash,
            'times': 10
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

    def VerifySignature(self, msg, r_plum, Knx, Kny):
        # 建立 ECC obj
        cliPub = ECC.EccPoint(Knx, Kny, curve='P-384')
        # 建立 msg hash
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # Calculate
        hKn = cliPub.__mul__(hm)
        rP = self.P.__mul__(r_plum)
        chash = hKn.__add__(rP)
        chash = (int(chash.x), int(chash.y))

        result = chash == self.sessionKeys[Knx]['Chash']
        print("[Line 67] CH: ", self.sessionKeys[Knx]['Chash'][0])
        print("[Line 68] CH(1): ", chash[0])
        print("[Line 69] Kn: ", Knx)
        print("[Line 70] hKn: ", int(hKn.x))
        print("[Line 71] rp: ", int(rP.x))
        print("[Line 72] hm: ", hm)
        return result

    def MakeSignature(self, msg, Knx):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        # calculate r
        sk = self.sessionKeys[Knx]['sk']
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)
        r = sk - hm * self.kn

        # Calculate
        hKn = self.Kn.__mul__(hm)
        rP = self.P.__mul__(r)
        chash = hKn.__add__(rP)
        chash = (int(chash.x), int(chash.y))
        return r
