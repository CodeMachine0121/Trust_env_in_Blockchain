from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from ecc.curve import Point, secp256k1


class Participator:
    def __init__(self):
        self.P = secp256k1.G
        self.q = secp256k1.p  # 曲線計算用的模數
        self.order = 115792089237316195423570985008687907852837564279074904382605163141518161494337  # order number
        # Key pair
        self.kn = int(getrandbits(512))
        self.Kn = self.P * self.kn

        self.sk = -1
        self.Chash = None

    def refreshSignatureKey(self, ):
        self.kn = int(getrandbits(512))
        self.Kn = self.P * self.kn
        print("[+] Refresh Signature Key")
        print("\t[-] Kn x: ", hex(self.Kn.x))
        print("\t[-] kn y: ", hex(self.kn.y))


    def start_SessionKey(self, z, xpx, xpy, servPubX):
        xP = Point(xpx, xpy, curve=secp256k1)
        self.sk = int((xP * z).x)
        print("[+] Setting sk: ")
        print("\tsk: ",hex(self.sk))
        # 初始化 變色龍雜湊
        self.init_CHash(self.sk)

        return

    def init_CHash(self, sk):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(b'Initialize')
        hm = int(H1.hexdigest(), 16)

        rP = ((sk - (hm * self.kn)) % self.order) * self.P
        hKn = self.Kn * hm
        self.Chash = hKn + rP

        print("\t[-] Chameleon Hash: ")
        print("\t\tx: ", hex(self.Chash.x))
        print("\t\ty: ", hex(self.Chash.y))

        return

    def VerifySignature(self, msg, r_plum, servPubX, servPubY):
        # 建立 ECC obj
        serv = Point(servPubX, servPubY, curve=secp256k1)
        # 建立 msg hash
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        # Calculate
        hKn = serv * hm
        rP = self.P * r_plum
        chash = hKn + rP
        print("[+] Calculate Hash: \n\tx:{}\n\ty:{}".format(hex(chash.x), hex(chash.y)))
        result = chash == self.Chash
        return result

    def MakeSignature(self, msg):
        # Hash function obj
        H1 = HMAC.new(b'', digestmod=SHA256)

        # calculate r
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)
        r = (self.sk - (hm * self.kn)) % self.order
        print("[+] Calculate Signature: \n\t{}".format(hex(r)))
        return r

    def verifyTransactionSignature(self, msgs, CHashX, CHashY, Knx, Kny, signatures):
        print("[+] Verify the Txn Signature")
        senderAG = Point(Knx, Kny, curve=secp256k1)
        chash = Point(CHashX, CHashY, curve=secp256k1)
        print("\t[-] AG(Sender)'s Kn: ")
        print("\t\tx: ", hex(Knx))
        print("\t\ty: ", hex(Kny))
        print("\t[-] sender's CH: ")
        print("\t\tx: ",hex(CHashX))
        print("\t\ty: ", hex(CHashY))
        print("\n")

        for i in range(0, len(signatures)):
            if signatures[i] == 0:
                continue
            print("\t[-] r: ", hex(signatures[i]))
            print("\t[-] txn msg: ", msgs[i])
            H1 = HMAC.new(b'', digestmod=SHA256)
            H1.update(msgs[i].encode())
            hm = int(H1.hexdigest(), 16)

            hkn = senderAG * hm
            rP = self.P * signatures[i]

            _chash = hkn + rP

            if chash != _chash:
                print("[!]Failed: [{}/{}]".format(i + 1, len(msgs)))
                return False
        print("\t[-]Verify Result: True")
        return True

    def verifyPaymentSignature(self, msg, CHashX, CHashY, Knx, Kny, signatures):
        print("[+] Verify the payment Txn Signature")
        PubKey = Point(Knx, Kny, curve=secp256k1)

        print("\t[-] AG(Sender)'s Kn: ")
        print("\t\tx: ", hex(Knx))
        print("\t\ty: ", hex(Kny))
        print("\t[-] sender's CH: ")
        print("\t\tx: ", hex(CHashX))
        print("\t\ty: ", hex(CHashY))
        print("\t[-] r: ", hex(signatures))
        print("\t[-] txn msg: ", msgs)

        H1 = HMAC.new(b'', digestmod=SHA256)
        H1.update(msg.encode())
        hm = int(H1.hexdigest(), 16)

        hKn = PubKey * hm
        rP = self.P * signatures
        chash = hKn + rP

        CHash = Point(CHashX, CHashY, curve=secp256k1)

        return chash == CHash
