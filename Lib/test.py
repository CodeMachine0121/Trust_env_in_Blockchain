import math
import time

from ecc.curve import Point
from ecc.curve import secp256k1 as S256
from Crypto.Hash import HMAC, SHA256
from Crypto.Random.random import getrandbits


def sessionKey():
    # jet
    p = S256.G

    timeLoop = [i for i in range(10, 110, 10)]
    timeList = []
    da = int(getrandbits(512))
    db = int(getrandbits(512))
    otp = int(getrandbits(512))
    for t in timeLoop:
        counter = 0

        for i in range(t):
            daP = da * p
            counter += int(math.log2(da)) + 1
            dbdaP = db * daP
            counter += int(math.log2(db)) + 1
            sk = dbdaP.x ^ otp
            counter += 1

        timeList.append(counter)
    print(timeList)


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


def normalPow(under, upper):
    sum = 0
    counter = 1
    for i in range(upper):
        counter += 1
        for j in range(under):
            sum += under
            counter += 2
        counter += 1
    return counter


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


def test():

    counterList = []
    counter = 1
    for t in range(100):
        for i in range(100):
            counter += 1
            for j in range(100):
                counter += 2
            counter += 1
        counterList.append(counter)
    print(counterList)

    counterList = []
    counter = 0
    for i in range(100):
        n = 100
        while n>0:
            counter+=1
            n/=2
        counterList.append(counter)
    print(counterList)
    return


if __name__ == '__main__':
    test()

    #sessionKey()
