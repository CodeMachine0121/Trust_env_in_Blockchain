from ecc.curve import secp256k1 as s256
from ecc.curve import Point
import hashlib, random, string
from Crypto.Random.random import getrandbits

P = s256.G
print("[+]P: \n\tx: {}\n\ty: {}".format(P.x,P.y))
q = s256.p
print("[+]q:\n\t {}".format(q))
k = int(getrandbits(2048)) 
print("[+]k: \n\t{}".format(k))
kn = int(getrandbits(2048))
print("[+]kn: \n\t{}".format(kn))
Kn = kn*P
print("[+]Kn: \n\tx: {}\n\ty: {}".format(Kn.x,Kn.y))

m = "Hello"
print("[+]msg: ", m)
hm = int(hashlib.sha256(m.encode()).hexdigest(),16)
print("[+]H(m): \n\t{}".format(hm))
print("#######################################################")

dn = (hm*(kn))

print("[+] order: 115792089237316195423570985008687907852837564279074904382605163141518161494337")
print("[+] modular: ", q)
rn = (k-dn)%(115792089237316195423570985008687907852837564279074904382605163141518161494337)
print("[+]rn: \n\t{}".format(rn))

print("#######################################################")
CH = hm*Kn+rn*P
print("[+]CH1: \n\tx: {}\n\ty: {}".format(CH.x,CH.y))

print("#######################################################")
end_correct = 0

####################
#
####################
for i in range(0,100):
    m2 = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(10))
    hm2 = int(hashlib.sha256(m2.encode()).hexdigest(), 16)

    dn = (hm2*kn)
    rn2 = (k-dn)
    CH2 = hm2*Kn+rn2*P
    
    if CH2 == CH:
        end_correct+=1
###########################
#
###########################
print("[+] correct / times = {}/{} = {}%".format(end_correct, 100, end_correct))






