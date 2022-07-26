import math
import string
import time
import random

import sympy
from Crypto.Util.number import inverse
from Crypto.Hash import HMAC, SHA256
import hashlib


def simpleExample():
    n = 3233
    phin = 3120
    e = 17
    d = inverse(e, phin)
    x = 8
    en = pow(x, e) % n
    print(en)
    de = pow(en, d) % n
    print(de)


def generate_prime(leng):
    return sympy.randprime(2 ** leng, 2 ** (leng + 10))


def mod_powMSb(key, msg, n):
    e = bin(key)[2:]
    y = 1
    counter = 1

    for i in range(len(e)):
        y = (y * y) % n
        counter += 2
        if e[i] == '1':
            y = y * msg % n
            counter += 2
        counter += 1
    return y, counter


class rsaBase:
    def __init__(self, ID, msg, leng):
        self.p = generate_prime(leng)
        self.q = generate_prime(leng)
        self.n = self.p * self.q
        self.phi_n = (self.p - 1) * (self.q - 1)
        self.e = sympy.randprime(self.phi_n // 2, self.phi_n)
        self.d, _, gcd = sympy.gcdex(self.e, self.phi_n)
        self.d = (int(self.d + self.phi_n)) % self.phi_n
        self.ch = dict()
        self.extract(ID, msg)

    def extract(self, ID, msg):
        HID = int(hashlib.sha256(ID.encode()).hexdigest(), 16)
        self.ch["J"], c = mod_powMSb(self.d % self.phi_n, HID, self.n)
        self.ch["xID"] = sympy.randprime(self.phi_n // 2, self.phi_n)
        self.ch["PK"], c = mod_powMSb(self.ch["xID"] % self.phi_n, HID, self.n)

        ## calculate Hash value
        self.ch["r"] = sympy.randprime(self.phi_n // 2, self.phi_n)
        self.ch["hash"], c = self.hash(self.e, msg, self.ch['r'], self.ch["PK"])
        self.ch["msg"] = msg

    def hash(self, e, m, r, PK):
        hm = int(hashlib.sha256(m.encode()).hexdigest(), 16)
        counter = 1
        r_pow_e, c1 = mod_powMSb(e, r, self.n)
        pk_pow_hm, c2 = mod_powMSb(hm, PK, self.n)

        counter += c1
        counter += c2
        counter += 2
        return (r_pow_e * pk_pow_hm) % self.n, counter

    def forge(self, J, x, r, mPlum):
        counter = 0
        hm_plum = int(hashlib.sha256(mPlum.encode()).hexdigest(), 16)
        hm = int(hashlib.sha256(self.ch["msg"].encode()).hexdigest(), 16)
        counter += 2

        xh = x * (hm - hm_plum)
        counter += 3

        k, c = mod_powMSb(xh, J, self.n)
        counter += c

        r_p = r * k % self.n
        counter += 2

        return r_p, counter

    def verify(self, r_p, e, PK, m):
        hash_p, counter = self.hash(e, m, r_p, PK)
        return self.ch["hash"] == hash_p, counter


if __name__ == '__main__':
    strID = "This is my ID"
    signMsg = "Hello"
    signature = -1

    rsa = rsaBase(strID, "Firstmsg", 512)

    loopTime = [i for i in range(10, 110, 10)]
    timeList = []

    for t in loopTime:
        counter = 0
        for i in range(t):
            signature, c = rsa.forge(rsa.ch["J"], rsa.ch['xID'], rsa.ch['r'], signMsg)
            counter += c
        timeList.append(counter)
    print(timeList)
    print("----------------------------------------")

    timeList = []
    for t in loopTime:
        counter = 0
        for i in range(t):
            result, c = rsa.verify(signature, rsa.e, rsa.ch["PK"], signMsg)
            counter += c
        timeList.append(counter)
    print(timeList)
