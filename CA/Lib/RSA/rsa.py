from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class RSA_Library:
    def __init__(self):
        self.key = RSA.generate(2048)
        
        # public key
        self.publicKey = self.key.publickey().export_key()

    
    def EncryptFunc(self,msg):
        cipherRSA=PKCS1_OAEP.new(self.publicKey)
        msg = msg.encode()
        enContent = cipherRSA.encrypt(msg)

        return enContent


    


