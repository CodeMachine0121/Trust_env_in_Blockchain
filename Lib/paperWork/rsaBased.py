import time

import sympy
from Crypto.Util.number import inverse
from Crypto.Hash import HMAC, SHA256
import hashlib
import numpy


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


def generate_prime():
    return sympy.randprime(2 ** 511, 2 ** 512)


def mod_powMSb(key, msg, n):
    e = bin(key)[2:]
    y = 1
    for i in range(len(e)):
        y = (y * y) % n
        if e[i] == '1':
            y = y * msg % n
    return y


class rsaBase:
    def __init__(self, ID, msg):
        p = generate_prime()
        q = generate_prime()
        self.n = p * q
        self.phi_n = (p - 1) * (q - 1)
        self.e = sympy.randprime(self.phi_n // 2, self.phi_n)
        self.d, _, gcd = sympy.gcdex(self.e, self.phi_n)
        self.d = int(self.d)
        self.ch = dict()
        self.extract(ID, msg)

    def extract(self, ID, msg):
        HID = int(hashlib.sha256(ID.encode()).hexdigest(), 16)
        self.ch["J"] = mod_powMSb(self.d % self.phi_n, HID, self.n)
        self.ch["xID"] = sympy.randprime(self.phi_n // 2, self.phi_n)
        self.ch["PK"] = mod_powMSb(self.ch["xID"] % self.phi_n, HID, self.n)

        ## calculate Hash value
        self.ch["r"] = sympy.randprime(self.phi_n // 2, self.phi_n)
        self.ch["hash"] = self.hash(self.e, msg, self.ch['r'], self.ch["PK"])
        self.ch["msg"] = msg

    def hash(self, e, m, r, PK):
        hm = int(hashlib.sha256(m.encode()).hexdigest(), 16)
        r_pow_e = mod_powMSb(e % self.phi_n, r, self.n)
        pk_pow_hm = mod_powMSb(hm % self.phi_n, PK, self.n)
        return (r_pow_e * pk_pow_hm) % self.n

    def forge(self, J, x, r, mPlum):
        H0 = HMAC.new(b'H0', digestmod=SHA256)
        H0.update(mPlum.encode())
        hm_plum = int(hashlib.sha256(mPlum.encode()).hexdigest(), 16)
        hm = int(hashlib.sha256(self.ch["msg"].encode()).hexdigest(), 16)

        r_p = r * mod_powMSb(x * (hm - hm_plum) % self.phi_n, J, self.n) % self.n
        return r_p

    def verify(self, r_p, e, PK, m):
        hash_p = self.hash(e, m, r_p, PK)
        return self.ch["hash"] == hash_p


if __name__ == '__main__':
    strID = "This is my ID"

    signMsg = "1234"
    rsa = rsaBase(strID, "Firstmsg")

    signatures = list()
    for i in range(0, 100):
        rp = rsa.forge(rsa.ch["J"], rsa.ch['xID'], rsa.ch['r'], signMsg)

        signatures.append(rp)

    verifyCostTime = list()
    start = time.time()
    for i in range(0, 100):
        rsa.verify(signatures[i], rsa.e, rsa.ch["PK"], signMsg)
        if (i + 1) % 10 == 0:
            verifyCostTime.append(time.time() - start)

    with open("verifyTime.txt", 'w') as file:
        for t in verifyCostTime:
            file.write("{},".format(t))
        file.close()
