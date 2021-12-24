from ecc.curve import Point
from ecc.curve import secp256k1 as S256
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits


class Participator:
    def __init__(self, k):
        print("[+] generating System parameters")
        self.P = S256.G
        self.Px = self.P.x
        self.Py = self.P.y
        
        self.q = S256.p # 曲線計算的模數
        # order number
        self.order = 115792089237316195423570985008687907852837564279074904382605163141518161494337
       
        # secret values
        #self.k = int(getrandbits(2048))
        self.k = k
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
        r = (self.k - (hm*self.kn)) % self.order
        return ((hm*self.Kn) + (r * self.P))
    
    def Signing(self, msg:str ):
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        
        hm = int(H1.hexdigest(), 16)
        r = (self.k - (hm * self.kn)) % self.order
        print("[+] Calculate Signature: \n\t{}".format(r))
        return r
    
    def Verifying(self, msg, r_plum, CA_Knx, CA_Kny):
        # restore Signer's PublicKey
        Kn = Point(CA_Knx, CA_Kny, curve=S256)
        
        # calculate Hash value
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # calculate r value
        rP = self.P * r_plum
        CH = Kn * hm + rP

        print("[+] Calculate Hash: \n\tx:{}\n\ty:{}".format(CH.x, CH.y) )
        return self.CHash == CH
        
    
