from Participator import Participator
from Verifier import Verifier
import time

ver = Verifier()
Px = int(ver.P.x)
Py = int(ver.P.y)

msg = 'Hello'
signatures=[]
cost=[]

for i in range(1,101):
    vr = ver.Signing(msg)
    signatures.append(vr)

part = Participator(ver.k)
start = time.time()
for i in range(0,100):
    s = part.Verifying(msg, signatures[i], ver.Kn.x, ver.Kn.y)
    if (i+1)%10 == 0 :
        cost.append(time.time()-start)

counter=1
for t in cost:
    print("[+] {}: {}".format(counter*10,t))
    counter+=1


