from ecc.curve import Point
from ecc.curve import secp256k1 as S256
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
import time


class Verifier:
    def __init__(self, k):
        print("[+] Importing System parameters (for Client)")
        self.P = S256.G
        self.Px = self.P.x
        self.Py = self.P.y

        self.q = S256.p  # 曲線計算的模數

        # Order number
        self.order = 115792089237316195423570985008687907852837564279074904382605163141518161494337

        self.x = int(getrandbits(512))
        self.xP = self.P * self.x
        self.PrintSystemParameters()

        # secret values      
        self.kn = int(getrandbits(512))
        # public value (向量點乘)
        self.Kn = self.kn * self.P
        self.PrintSignaturePublicKey()

        # 紀錄多個使用者資訊
        self.sessionKeys = dict()

    def refresh_KeyPair(self, ):
        self.kn = int(getrandbits(512))
        self.Kn = self.kn * self.P
        self.PrintSignaturePublicKey()


    def start_SessionKey(self):
        return int(self.xP.x), int(self.xP.y)

    def set_SessionKey(self, zpx, zpy, Cli_PubX, chain_Address):
        print("[+] client: {} Registering".format(chain_Address))
        zP = Point(zpx, zpy, curve=S256)
        sk = int((zP * self.x).x)
        print("\t[-] Session Key:\n\t\t{}".format(hex(sk)))

        # 初始化變色龍雜湊跟使用者紀錄
        Chash = self.init_Hash(sk)

        # address as index
        self.sessionKeys[chain_Address] = {
            "cliPub": Cli_PubX,
            "sk": sk,
            "Chash": Chash,
            "times": time.time()
        }

        return

    def init_Hash(self, sk):
        print("[+] Initializing Chameleon Hash")
        msg = b'inittailize'
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg)
        hm = int(H1.hexdigest(), 16)
        r = (sk - (hm * self.kn)) % self.order
        hash = ((hm * self.Kn) + (r * self.P))

        print("\t[-] Chameleon Hash: ")
        print("\t\tx: ", hex(hash.x))
        print("\t\ty: ", hex(hash.y))
        return hash

    def Signing(self, msg: str, address: str):
        print("[+] Client: {}  ask for Signature".format(address))
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        sk = self.sessionKeys[address]["sk"]
        r = (sk - (hm * self.kn)) % self.order
        print("[+] Calculate Signature: \n\t{}".format(hex(r)))
        return r

    def Verifying(self, msg, r_plum, Knx, Kny, address):
        # restore Signer's PublicKey
        print("[+] Verify msg from Client: {} ".format(address))
        Kn = Point(Knx, Kny, S256)

        # calculate Hash value
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # calculate r value
        rP = self.P * r_plum
        CH = Kn * hm + rP

        # CH in AG
        CH2 = self.sessionKeys[address]["Chash"]
        print("[+] Calculate Hash: \n\tx:{}\n\ty:{}".format(hex(CH.x), hex(CH.y)))
        return CH2 == CH

    def PrintSystemParameters(self):
        print("[+] System Parameters: ")
        print("\t[-] P: ")
        print("\t\tx:", hex(self.P.x))
        print("\t\ty:", hex(self.P.y))
        print("\t[-] q: ")
        print("\t\t", hex(S256.n))

    def PrintSignaturePublicKey(self):
        print("[+] Using Signature Key Kn: ")
        print("\tx: ", hex(self.Kn.x))
        print("\ty: ", hex(self.Kn.y))
