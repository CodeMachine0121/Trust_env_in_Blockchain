# coding:utf-8

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os
from os.path import join
class RSA_Library:
    def __init__(self):
        # check if keyfile exist
        if 'RSA_keystore'  not in os.listdir() or len(os.listdir('RSA_keystore'))==0:
            
            try:
                os.mkdir('RSA_keystore') # create folder to save rsa keys
            except:
                pass
            ## create key pair
            # private key
            self.privateKey = RSA.generate(2048)
            # public key
            self.publicKey = self.privateKey.publickey()
            self.BackupKey()


        else:
            self.privateKey, self.publicKey = self.ImportKey()

    def BackupKey(self):
        secretCode = 'codeToreadKey'
        ##  寫成文件的時候要以祕文儲存
        private = self.privateKey.export_key(passphrase=secretCode, pkcs=8, protection="scryptAndAES128-CBC")
        
        #  寫入文件
        path = join('.','RSA_keystore')
        with open(join(path,"private.pem"), "wb") as f:
            f.write(private)
        return 

    def ImportKey(self):
        secretCode = 'codeToreadKey'
        # 讀取金鑰文件i
        path = join('.','RSA_keystore')
        encodedKey = open(join(path,'private.pem'), 'rb').read()

        privateKey = RSA.import_key(encodedKey, passphrase=secretCode)
        publicKey = privateKey.publickey()
        return privateKey, publicKey
    
    

    def EncryptFunc(self,msg, publicKey):
        
        ##  匯入接收方公鑰
        
        strpub = '-----BEGIN PUBLIC KEY-----\n'+publicKey+'\n-----END PUBLIC KEY-----'
        public = RSA.import_key(strpub.encode('utf-8'))

        cipherRSA=PKCS1_OAEP.new(public)
        msg = msg.encode()
        enContent = cipherRSA.encrypt(msg)

        return enContent.hex()
    


    def DecryptFunc(self, encrypted_msg):
        encrypted_msg = bytes.fromhex(encrypted_msg)
        cipherRSA = PKCS1_OAEP.new(self.privateKey)
        encodedMsg = cipherRSA.decrypt(encrypted_msg)
        
        msg = encodedMsg.decode()
        return msg



    def OutputPublic(self):
        return self.publicKey.export_key().decode().replace('-----BEGIN PUBLIC KEY-----\n','').replace('\n-----END PUBLIC KEY-----','')
