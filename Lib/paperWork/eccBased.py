from ecc.curve import secp256k1 as S256
from Crypto.Random.random import getrandbits

import hashlib
import time
import math


def inverse(u, v):
    """The inverse of :data:`u` *mod* :data:`v`."""

    u3, v3 = u, v
    u1, v1 = 1, 0
    counter = 0
    while v3 > 0:
        q = u3 // v3
        u1, v1 = v1, u1 - v1 * q
        u3, v3 = v3, u3 - v3 * q
        counter += 5

    while u1 < 0:
        u1 = u1 + v
        counter += 1
    # 時間複雜度為 O(log n)
    return u1, counter


class eccBase:
    def __init__(self, msg, leng):
        self.P = S256.G
        self.q = S256.p  # 橢圓計算用模數
        # order number
        self.order = 115792089237316195423570985008687907852837564279074904382605163141518161494337

        ## TK
        self.k = int(getrandbits(leng))
        self.x = int(getrandbits(leng))

        ## HK
        self.K = self.k * self.P
        self.Y = self.x * self.P

        self.r = int(getrandbits(512))
        self.Hash, c = self.hash(msg, self.r)
        self.m1 = msg

    def hash(self, m, r):
        counter = 0
        hmK = int(hashlib.sha256(m.encode()).hexdigest(), 16)
        counter += 1

        hmkK = (hmK * self.K)
        krY = (self.k * r * self.Y)

        h = (hmK * self.K) + (self.k * r * self.Y)
        counter += int(math.log2(hmK))
        counter += int(math.log2(self.k * r))
        counter += int(math.log2(int(abs((hmkK.x - krY.x) / (hmkK.y - krY.y)))))
        return h, counter

    def forge(self, m2):
        counter = 0
        hm1 = int(hashlib.sha256(self.m1.encode()).hexdigest(), 16)
        counter += 1
        hm2 = int(hashlib.sha256(m2.encode()).hexdigest(), 16)
        counter += 1

        inv, c = inverse(self.x, self.order)
        counter += c

        rp = (self.r + inv * (hm1 - hm2)) % self.order
        counter += 4

        return rp, counter

    def verify(self, m2, rp):
        hp, counter = self.hash(m2, rp)
        result = hp == self.Hash
        return result, counter


if __name__ == '__main__':

    eccKey = eccBase("First", 512)
    secondmsg = 'hello'
    rp = -1

    loopTime = [i for i in range(10, 110, 10)]
    timeList = []

    for t in loopTime:
        counter = 0
        for i in range(t):
            rp, c = eccKey.forge(secondmsg)
            counter += c
        timeList.append(counter)
    print(timeList)
    print("--------------------------")

    timeList = []
    for t in loopTime:
        counter = 0
        for i in range(t):
            result, c = eccKey.verify(secondmsg, rp)
            counter += c
        timeList.append(counter)
    print(timeList)
