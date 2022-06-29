from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random.random import getrandbits
from Crypto.Random import get_random_bytes
import hashlib
import struct


class AES_Library:
    def __init__(self, SK: int):
        hexSK = hex(SK)
        self.key = bytes.fromhex(hexSK[2:]) # 256-bit

    def Encrypt(self, data: str) -> str:
        cipher = AES.new(self.key, AES.MODE_CBC)
        cipheredData = cipher.encrypt(pad(data.encode(), AES.block_size))
        return cipheredData, cipher.iv

    def Decrypt(self, enMsg: bytes, iv: bytes) -> str:
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        deMsg = cipher.decrypt(enMsg)
        MsgUnpadding = unpad(deMsg,AES.block_size)
        return MsgUnpadding


if __name__ == '__main__':
    sk = 111860730450424479710817257937831320421188514328189455301977012854312665853841
    iv = int(getrandbits(16))

    aes = AES_Library(sk)

    msg = "Hello"
    enMsg, iv = aes.Encrypt(msg)
    print("[+] EnMsg: ", enMsg)

    deMsg = aes.Decrypt(enMsg, iv)
    print("[+] DeMsg: ", deMsg)
