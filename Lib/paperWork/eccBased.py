from ecc.curve import secp256k1 as S256
from Crypto.Random.random import getrandbits
from Crypto.Util.number import inverse
import matplotlib.pyplot as plt
import hashlib
import time


class eccBase:
    def __init__(self, msg):
        self.P = S256.G
        self.q = S256.p  # 橢圓計算用模數
        # order number
        self.order = 115792089237316195423570985008687907852837564279074904382605163141518161494337

        ## TK
        self.k = int(getrandbits(512))
        self.x = int(getrandbits(512))

        ## HK
        self.K = self.k * self.P
        self.Y = self.x * self.P

        self.r = int(getrandbits(512))
        self.Hash = self.hash(msg, self.r)
        self.m1 = msg

    def hash(self, m, r):
        hmK = int(hashlib.sha256(m.encode()).hexdigest(), 16)
        return (hmK * self.K) + (self.k * r * self.Y)

    def forge(self, m2):
        hm1 = int(hashlib.sha256(self.m1.encode()).hexdigest(), 16)
        hm2 = int(hashlib.sha256(m2.encode()).hexdigest(), 16)

        return (self.r + inverse(self.x, self.order) * (hm1 - hm2)) % self.order

    def verify(self, m2, rp):
        return self.hash(m2, rp) == self.Hash


if __name__ == '__main__':
    eccbase = eccBase("First")

    secondmsg = "Second"

    forgeCostTime = list()
    start = time.time()
    for i in range(0, 100):
        rp = eccbase.forge(secondmsg)
        if (i + 1) % 10 == 0:
            forgeCostTime.append(time.time()-start)
    with open("forgeCostTime.txt", 'w') as file:
        for t in forgeCostTime:
            file.write(str(t)+",")
        file.close()

    print()
