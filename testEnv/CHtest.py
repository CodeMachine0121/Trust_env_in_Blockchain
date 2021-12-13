from ecc.curve import secp256k1 as s256
from ecc.curve import Point
import hashlib
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
rn = (k-dn)
print("[+]rn: \n\t{}".format(rn))

print("#######################################################")
CH = hm*Kn+rn*P
print("[+]CH1: \n\tx: {}\n\ty: {}".format(CH.x,CH.y))

print("#######################################################")
m2 = "World"
print("[+]msg2: ",m2)
hm2 = int(hashlib.sha256(m2.encode()).hexdigest(), 16)
print("[+]H(m2): \n\t{}".format(hm2))

dn = (hm2*kn)
rn2 = (k-dn)
print("[+]rn2: \n\t{}".format(rn2))
CH2 = hm2*Kn+rn2*P
print("[+]CH2: \n\tx: {}\n\ty: {}".format(CH2.x,CH2.y))

print("[+] CH1 == CH2: ", CH==CH2)






