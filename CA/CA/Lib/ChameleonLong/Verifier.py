from ecc.curve import Point
from ecc.curve import secp256k1 as S256
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits


class Verifier:
    def __init__(self):
        print("[+] Generating System parameters")
        self.P = S256.G
        self.Px = self.P.x
        self.Py = self.P.y

        self.q = S256.p  # 橢圓計算用模數
        # order number
        self.order = 115792089237316195423570985008687907852837564279074904382605163141518161494337

        # secret values
        self.k = int(getrandbits(512))
        self.kn = int(getrandbits(512))

        # public value (向量點乘)
        self.Kn = self.kn * self.P

        # calculate chameleon Hash
        self.CHash = self.init_Hash()
        self.PrintSystemParameters()

    def init_Hash(self):
        print("[+] Initializing Chameleon Hash")
        msg = b'inittailize'
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg)
        hm = int(H1.hexdigest(), 16)
        r = (self.k - (hm * self.kn)) % self.order
        hash = ((hm * self.Kn) + (r * self.P))
        print("\t[-] Chameleon Hash: ")
        print("\t\tx: ", hex(hash.x))
        print("\t\ty: ", hex(hash.y))
        return hash

    def Signing(self, msg: str):
        self.PrintSignaturePubliKey()
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())

        hm = int(H1.hexdigest(), 16)
        r = (self.k - (hm * self.kn)) % self.order
        print("[+] Calculate Signature: \n\t{}".format(hex(r)))
        return r

    def Verifying(self, msg, r_plum, Knx, Kny):
        # restore Signer's PublicKey
        Kn = Point(Knx, Kny, S256)

        # calculate Hash value
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # calculate r value
        rP = self.P * r_plum
        CH = Kn * hm + rP

        print("[+] Calculate Hash: \n\tx:{}\n\ty:{}".format(hex(CH.x), hex(CH.y)))
        return self.CHash == CH

    def PrintSystemParameters(self):
        print("[+] System Parameters: ")
        print("\t[-] P: ")
        print("\t\tx:", hex(self.P.x))
        print("\t\ty:", hex(self.P.y))
        print("\t[-] q: ")
        print("\t\t", hex(S256.n))

    def PrintSignaturePubliKey(self):
        print("[+] Using Signature Key Kn: ")
        print("\tx: ", hex(self.Kn.x))
        print("\ty: ", hex(self.Kn.y))
