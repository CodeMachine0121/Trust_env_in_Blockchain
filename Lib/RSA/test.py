import math
import string
import time
import random

import sympy
from Crypto.Util.number import inverse
from Crypto.Hash import HMAC, SHA256
import hashlib


def generate_prime(leng):
    return sympy.randprime(2 ** leng, 2 ** (leng + 10))


# key 指數
def mod_powMSb(key, msg, n):
    e = bin(key)[2:]
    y = 1
    counter = 1

    for i in range(len(e)):
        counter += 1
        y = (y * y) % n
        counter += 2
        if e[i] == '1':
            y = y * msg % n
            counter += 2
    return y, counter


class RSA:
    def __init__(self, leng):
        p = generate_prime(leng)
        q = generate_prime(leng)
        #p=int("0x377673ac1bd3cc439a8d5110da36952ab6950bdcfca24c7cab41a551a77af8db49a0b90c12c177f24d11e8ea213a86df383784d1bdeaa5f10de10155518ad3f54bb",16)
        #q= int("0x19a12abd37d8b81c360059e78e25005eb734bacf15656974517ffa46290899d32cb5bf01bce11b7cf2f0841e50fc0073fc8497b72bb1605ba808c8b50b71fe8a3cd",16)

        self.n = p * q
        self.phi_n = (p - 1) * (q - 1)
        #self.e = int("0x44d3cb52fcf496eff6673ec962bed19c73c6a25cea82fa414220bb67e40ecf35351145380ea9770d1237b2f385aa7a39feca462d77a2c4024882f6318419e77dc30aa3b93261cc0ca964e0931d13cdf388e29db4d664b4423fe556f37e232e179743f8e871715e6edea172ea39c1455e9fcf798a5b3d9724d230c9ba30dc1cb8c329d",16)
        #self.d = int("0xafc2f214b87f5d372678539e80cbbcc5c5aac11ee91b6d78ff76f1096e904a80aee375c9e1df242053713a8779b42bddd314de98c2fab8699209aec284d4544fe6626c0e2b36ce1a54bdd9193007ba358ea9e7c3bcd0e9af1ddd9ef13860f84cc2800fb4b798337ec87450b27b4281eb96ddf4e8f94f9cedb4de0175f11c4f045253", 16)
        self.e = sympy.randprime(self.phi_n//2, self.phi_n)
        self.d, _, gcd = sympy.gcdex(self.e, self.phi_n)
        self.d = (int(self.d+self.phi_n))%self.phi_n


    def sign(self, msg: str, key):
        counter = 0
        msg = msg.encode()
        hm = int(hashlib.sha256(msg).hexdigest(), 16)
        counter += 1

        signature, c = mod_powMSb(key, hm, self.n)
        counter += c
        print(len(bin(key)))
        return signature, counter

    def verify(self, msg: str, signature: int):

        hhm,c = mod_powMSb(self.e, signature, self.n)

        hm = int(hashlib.sha256(msg.encode()).hexdigest(), 16)
        c+=1
        result = hm == hhm
        return result, c

def test():
    rsa = RSA(512)
    cipher, c = rsa.sign("Hello", rsa.d)
    result, c = rsa.verify("Hello", cipher)
    print(result)
    c = 123
    a, v = mod_powMSb(rsa.d, c, rsa.n)
    b, v = mod_powMSb(rsa.e, a, rsa.n)
    print(b)

if __name__ == '__main__':

    rsa = RSA(512)
    timeList = []
    loopTime = [i for i in range(10, 110, 10)]

    sign = -1
    for t in loopTime:
        counter = 1
        for i in range(t):
            sign, c = rsa.sign("hello", rsa.d)
            counter += c
        timeList.append(counter)
    print(timeList)
    print("---------------------")

    timeList = []
    for t in loopTime:
        counter = 1
        for i in range(t):
            result, c = rsa.verify("hello", sign)

            counter += c
            counter += 1
        timeList.append(counter)
    print(timeList)


