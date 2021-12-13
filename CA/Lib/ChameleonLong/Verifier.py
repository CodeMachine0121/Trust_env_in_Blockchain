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
        
        self.q = S256.p # order number

        # secret values
        self.k = int(getrandbits(2048))
        self.kn = int(getrandbits(2048)) 

        # public value (向量點乘)
        self.Kn = self.kn * self.P
        
        # calculate chameleon Hash
        self.CHash = self.init_Hash() 

    def init_Hash(self):
        print("[+] Initializing Chameleon Hash")
        msg = b'inittailize'
        H1 = HMAC.new(b'', digestmod = SHA256)
        H1.update(msg)
        hm = int(H1.hexdigest(), 16)
        r = (self.k - (hm*self.kn))
        return ((hm*self.Kn) + (r * self.P))
    
    def Signing(self, msg:str):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        
        hm = int(H1.hexdigest(), 16)
        r = (self.k - (hm * self.kn))
        print("[+] Calculate Signature: \n\t{}".format(r))
        return r
    
    def Verifying(self, msg, r_plum, Knx, Kny):
        # restore Signer's PublicKey
        Kn = Point(Knx,Kny, S256)
        
        # calculate Hash value
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # calculate r value
        rP = self.P * r_plum
        CH = Kn * hm + rP

        print("[+] Calculate Hash: \n\tx:{}\n\ty:{}".format(CH.x, CH.y) )
        return self.CHash == CH
        
    
