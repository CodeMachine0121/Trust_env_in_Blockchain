from ecc.curve import Point
from ecc.curve import secp256k1 as S256
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
import math
import time


class Verifier:
    def __init__(self, leng):
        print("[+] Generating System parameters")
        self.P = S256.G
        self.Px = self.P.x
        self.Py = self.P.y

        self.q = S256.p  # 橢圓計算用模數
        # order number
        self.order = 115792089237316195423570985008687907852837564279074904382605163141518161494337

        # secret values
        self.k = int(getrandbits(leng))
        self.kn = int(getrandbits(leng))

        # public value (向量點乘)
        self.Kn = self.kn * self.P

        # calculate chameleon Hash
        self.CHash, c = self.init_Hash()

        ### 攻擊用

    def setTrapdoor(self, Kn):
        self.Kn = Kn
        self.k = int(getrandbits(512))

    def init_Hash(self):
        print("[+] Initializing Chameleon Hash")
        counter = 0
        msg = b'inittailize'
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg)
        hm = int(H1.hexdigest(), 16)
        counter += 1

        r = (self.k - (hm * self.kn)) % self.order
        counter += 3
        return (hm * self.Kn) + (r * self.P), counter

    def Signing(self, msg: str):
        counter = 0
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)
        counter += 1

        r = (self.k - (hm * self.kn)) % self.order
        counter += 3
        return r, counter

    def Verifying(self, msg, r_plum, Knx, Kny):
        # restore Signer's PublicKey
        Kn = Point(Knx, Kny, S256)

        counter = 0
        # calculate Hash value
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)
        counter += 1
        # calculate r value
        rP = self.P * r_plum
        KnHm = Kn * hm
        CH = KnHm + rP
        counter += int(math.log2(r_plum))
        counter += int(math.log2(hm))

        result = self.CHash == CH
        return result, counter
