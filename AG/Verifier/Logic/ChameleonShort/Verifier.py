from ecc.curve import Point
from ecc.curve import secp256k1 as S256
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits


class Verifier:
    def __init__(self, k):
        print("[+] Importing System parameters")
        self.P = S256.G
        self.Px = self.P.x
        self.Py = self.P.y
        
        self.q = S256.p # order number

        self.x = int(getrandbits(2048))
        self.xP = self.P*self.x

        # secret values      
        self.kn = int(getrandbits(2048)) 
        # public value (向量點乘)
        self.Kn = self.kn * self.P
        
        # 紀錄多個使用者資訊
        self.sessionKeys = dict()
 
    
    def start_SessionKey(self):
        return int(self.xP.x), int(self.xP.y)
    def set_SessionKey(self, zpx, zpy, Cli_PubX, chain_Address):
        print("[+] client: {} Registering".format(chain_Address))

        zP = Point(zpx, zpy, curve=S256)
        sk = int((zP*self.x).x)
        
        # 初始化變色龍雜湊跟使用者紀錄
        Chash = self.init_Hash(sk)
        print("\t[-] Session Key:\n\t{}".format(sk))
        print("\t[-] Session CH:\n\t x:{}\n\t y:{}".format(Chash.x, Chash.y))
        
        # address as index
        self.sessionKeys[chain_Address] = {
            "cliPub": Cli_PubX,
            "sk": sk,
            "Chash": Chash,
            "times": 10
        }
        
        return 

    def init_Hash(self, sk):
        print("[+] Initializing Chameleon Hash")
        msg = b'inittailize'
        H1 = HMAC.new(b'', digestmod = SHA256)
        H1.update(msg)
        hm = int(H1.hexdigest(), 16)
        r = (sk - (hm*self.kn))
        return ((hm*self.Kn) + (r * self.P))
    


    def Signing(self, msg:str, address:str):
        print("[+] Client: {}  ask for Signature".format(address))
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)
        
        sk = self.sessionKeys[address]["sk"]
        r = (sk - (hm * self.kn))
        print("[+] Calculate Signature: \n\t{}".format(r))
        return r
    
    def Verifying(self, msg, r_plum, Knx, Kny, address):
        # restore Signer's PublicKey
        print("[+] Verify msg from Client: {} ".format(address))
        Kn =Point(Knx,Kny, S256)
        
        # calculate Hash value
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # calculate r value
        rP = self.P * r_plum
        CH = Kn * hm + rP
        
        # CH in AG
        CH2 = self.sessionKeys[address]["Chash"] 
        print("[+] Calculate Hash: \n\tx:{}\n\ty:{}".format(CH.x, CH.y) )
        print("[+] Verifying result: {}".format(CH2 == CH))
        return CH2 == CH
        
    
