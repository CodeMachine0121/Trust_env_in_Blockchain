from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def Encrypt(key: int, data: str) -> (str, str):
    key = bytes.fromhex(hex(key)[2:])
    cipher = AES.new(key, AES.MODE_CBC)
    cipheredData = cipher.encrypt(pad(data.encode(), AES.block_size))
    return cipheredData.hex(), cipher.iv.hex()

def Decrypt(key: int, enMsg: str, iv: str) -> str:
    key = bytes.fromhex(hex(key)[2:])
    iv = bytes.fromhex(iv)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    deMsg = cipher.decrypt(bytes.fromhex(enMsg))
    MsgUnpadding = unpad(deMsg, AES.block_size)
    return MsgUnpadding.decode()
