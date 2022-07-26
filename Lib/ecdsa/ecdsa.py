from ecc.curve import Point
from ecc.curve import secp256k1 as S256
from Crypto.Hash import HMAC, SHA256
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
    # 時間複雜度為 O(n)
    return u1, counter


class ecdsa:
    def __init__(self, leng):
        self.P = S256.G
        # order number
        self.n = S256.n
        # keypair
        self.da = int(getrandbits(leng))
        self.HA = self.da * self.P

        # Signature keypair
        self.k = int(getrandbits(leng))
        self.Kn = self.k * self.P

    def sign(self, msg: str):
        counter = 0
        sha256 = hashlib.sha256()
        sha256.update(msg.encode())
        hm = int(sha256.hexdigest(), 16)
        counter += 1

        r = self.Kn.x % self.n
        counter += 1
        inv, c = inverse(self.k, self.n)
        counter += c
        s = inv * (hm + r * self.da) % self.n
        counter += 4
        return s, r, counter

    def verify(self, msg, s, r):
        counter = 0
        sha256 = hashlib.sha256()
        sha256.update(msg.encode())
        hm = int(sha256.hexdigest(), 16)
        counter += 1

        inv, c = inverse(s, self.n)
        counter += c

        u1 = (inv * hm) % self.n
        u2 = (inv * r) % self.n
        counter += 4

        u1P = u1 * self.P
        u2P = u2 * self.HA
        P = u1P + u2P
        counter += int(math.log2(u1))
        counter += int(math.log2(u2))

        lamb = (abs((u1P.x - u2P.x) / (u1P.y - u2P.y)))
        counter += int(math.log2(lamb))

        return (P.x % self.n) == (self.Kn.x % self.n), counter


if __name__ == '__main__':
    ecd = ecdsa(512)

    msg = 'hello'

    timeList = []
    loopTime = [i for i in range(10, 110, 10)]
    s = -1
    for t in loopTime:
        counter = 0
        for i in range(t):
            s, r, c = ecd.sign(msg)
            counter += c
        timeList.append(counter)
    print(timeList)
    print("--------------------------")

    timeList = []
    for t in loopTime:
        counter = 0
        for i in range(t):
            result, c = ecd.verify(msg, s, ecd.Kn.x % ecd.n)
            print(result)
            counter += c
        timeList.append(counter)
    print(timeList)
