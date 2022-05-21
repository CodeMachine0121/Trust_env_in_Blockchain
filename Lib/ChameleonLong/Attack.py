from Participator import Participator
from Verifier import Verifier
import time

ver = Verifier()
attackerVer = Verifier()


msg = 'Hello'
Orignal_signature = ver.Signing(msg)


times = 100000000
start = time.time()
for i in range(0, times):
    attackerVer.setTrapdoor(ver.Kn)
    attack_signature = attackerVer.Signing("Attack msg")
    print("[+] {} / {}".format(i+1, times))
    if attack_signature != Orignal_signature:
        print("\t[!] Verify Result: False")
    
    if attack_signature == Orignal_signature:
        print("[!] Break spend {} times".format(i+1))
        break
print("共耗時: {} 秒".format(time.time()-start))

#part = Participator(ver.k)
#s = part.Verifying(msg, signature, ver.Kn.x, ver.Kn.y)



