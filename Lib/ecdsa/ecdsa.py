from ecc.curve import Point
from ecc.curve import secp256k1 as S256
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits
from Crypto.Util.number import inverse
import hashlib
import time


class ecdsa:
    def __init__(self):
        self.P = S256.G
        # order number
        self.n = S256.n
        # keypair
        self.da = int(getrandbits(256))
        self.HA = self.da * self.P

        # Signature keypair
        self.k = int(getrandbits(256))
        self.Kn = self.k * self.P

    def sign(self, msg: str):
        sha256 = hashlib.sha256()
        sha256.update(msg.encode())
        hm = int(sha256.hexdigest(), 16)
        r = self.Kn.x % self.n
        s = inverse(self.k, self.n) * (hm + r * self.da) % self.n

        return s, r

    def verify(self, msg, s, r):
        sha256 = hashlib.sha256()
        sha256.update(msg.encode())
        hm = int(sha256.hexdigest(), 16)

        u1 = (inverse(s, self.n) * hm) % self.n
        u2 = (inverse(s, self.n) * r) % self.n

        P = u1 * self.P + u2 * self.HA

        return (P.x % self.n) == (self.Kn.x % self.n)


if __name__ == '__main__':
    ecd = ecdsa()
    msg = 'hello'

    signList = []
    for i in range(0, 100):
        s, r = ecd.sign(msg)
        signList.append(s)

    timeList = []
    start = time.time()
    for i in range(0, 100):
        if i % 10 == 0:
            timeList.append(time.time() - start)
        result = ecd.verify(msg, signList[i], ecd.Kn.x % ecd.n)

    with open("timefile.txt", 'w') as file:
        file.write(str(timeList))
