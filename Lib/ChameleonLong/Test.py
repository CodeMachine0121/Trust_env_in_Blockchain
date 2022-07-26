from Participator import Participator
from Verifier import Verifier
import time

if __name__ == '__main__':

    ver = Verifier(512)

    msg = 'Hello'
    signature = -1

    loopTime = [i for i in range(10, 110, 10)]
    timeList = []

    for t in loopTime:
        counter = 0
        for i in range(t):
            signature, c = ver.Signing(msg)
            counter += c
        timeList.append(counter)
    print(timeList)
    print("-----------")

    timeList = []
    for t in loopTime:
        counter = 0
        for i in range(t):
            s, c = ver.Verifying(msg, signature, ver.Kn.x, ver.Kn.y)
            counter += c
        timeList.append(counter)
    print(timeList)
