from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from ecc.curve import Point, secp256k1

class Verifier:
    def __init__(self):
        self.P = secp256k1.G
        self.q = secp256k1.p

        # Trap door key
        self.x = int(getrandbits(32))
        # Key pair
        self.kn = int(getrandbits(64))
        self.Kn = self.P*(self.kn)

        # Session key,  變色龍雜湊: 因為要記錄多個使用者所以用MAP紀錄
        self.sessionKeys = dict()

    def start_SessionKey(self):
        xP = self.P.__mul__(self.x)
        return int(xP.x), int(xP.y)

    def set_SessionKey(self, zpx, zpy, cli_PubX, chain_Address):
        zP = ECC.EccPoint(zpx, zpy, curve='P-384')
        sk = int(zP.__mul__(self.x).x)

        # 初始化 變色龍雜湊值
        Chash = self.init_CHash(sk)
        print("[Line 34] CH: ", Chash[0])
        print("[Line 35] SK: ", sk)
        # 用區塊鏈位址紀錄
        self.sessionKeys[chain_Address] = {
            "cliPub":cli_PubX,
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

    def VerifySignature(self, msg, r_plum, Knx, Kny, address):
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
        

        result = chash == self.sessionKeys[address]['Chash']
        print("[Line 67] CH: ", self.sessionKeys[address]['Chash'][0])
        print("[Line 68] CH(1): ", chash[0])
        print("[Line 69] Kn: ", Knx)
        print("[Line 70] hKn: ", int(hKn.x))
        print("[Line 71] rp: ", int(rP.x))
        print("[Line 72] hm: ", hm)
        return result

    def MakeSignature(self, msg, Knx, address):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        # calculate r
        sk = self.sessionKeys[address]['sk']
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)
        r = sk - hm * self.kn

        # Calculate
        hKn = self.Kn.__mul__(hm)
        rP = self.P.__mul__(r)
        chash = hKn.__add__(rP)
        chash = (int(chash.x), int(chash.y))
        return r
