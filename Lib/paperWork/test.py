import time


def inverse(u, v):
    """The inverse of :data:`u` *mod* :data:`v`."""

    u3, v3 = u, v
    u1, v1 = 1, 0
    print("[+] u1, v1: {}, {}".format(u1, v1))
    print("[+] u3, v3: {}, {}".format(u3, v3))
    counter = 1
    while v3 > 0:
        q = u3 // v3
        print("[+] Round ", counter)
        print("\t[-] q: ", q)
        print("\t[-] u1, v1: {}, {}".format(u1, v1))
        print("\t[-] u3, v3: {}, {}".format(u3, v3))

        u1, v1 = v1, u1 - v1 * q
        u3, v3 = v3, u3 - v3 * q

        counter += 1

    counter = 1
    while u1 < 0:
        print("[+] Round ", counter)
        u1 = u1 + v
        print("\t[-] u1: ", u1)
    # 時間複雜度為 O(log n)
    return u1


def mod_powMSb(msg, key):
    e = bin(key)[2:]
    y = 1
    for i in range(len(e)):
        y = (y * y)
        if e[i] == '1':
            y = y * msg
    # 時間複雜度為 O(n)
    return y


if __name__ == '__main__':

    n = 100
    timelist2 = []
    start = time.time()
    for i in range(0, n):
        if (i + 1) % 10 == 0:
            timelist2.append(time.time() - start)
        x = mod_powMSb(120, 123121)

    timelist = []
    start = time.time()
    for i in range(0, n):
        if (i + 1) % 10 == 0:
            timelist.append(time.time() - start)
        x = inverse(12, 123121)
    print(timelist)
    print(timelist2)
