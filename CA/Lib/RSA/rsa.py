from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class RSA_Library:
    def __init__(self):
        self.Key = RSA.generate(2048)
        
        # public key
        self.publicKey = self.Key.publickey()
    
    def BackupKey(self):
        secretCode = 'codeToreadKey'
        ##  寫成文件的時候要以祕文儲存
        private = self.Key.export_key(passphrase=secretCode, pkcs=8, protection="scryptAndAES128-CBC")
        
        #  寫入文件
        with open("private.pem", "wb") as f:
            f.write(private)

    def ImportKey(self)
        secretCode = 'codeToreadKey'
        # 讀取金鑰文件
        encodedKey = open('private.pem', 'rb').read()

        self.Key = RSA.import_key(encodedKey, passphrase=secretCode)
        self.pbulicKey = self.Key.publicKey()


    def EncryptFunc(self,msg, publicKey):
        
        ##  匯入接收方公鑰
        public = RSA.import_key(publicKey.encode('utf-8'))

        cipherRSA=PKCS1_OAEP.new(self.publicKey)
        msg = msg.encode()
        enContent = cipherRSA.encrypt(msg)

        return enContent
    
    def DecryptFunc(self, encrypted_msg):
        cipherRSA = PKCS1_OAEP.new(self.private)
        encodedMsg = cipherRSA.decrypt(encrypted_msg)
        
        msg = encodedMsg.decode()
        return msg




    


