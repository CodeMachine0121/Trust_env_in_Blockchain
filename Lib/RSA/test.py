from Crypto.PublicKey import RSA
from hashlib import sha512
import time


keyPair = RSA.generate(bits=1024)
cost=[]
msg = b'test message'
signatures=[]

start = time.time()
for i in range(1,101):
    hash = int.from_bytes(sha512(msg).digest(), byteorder='big')
    signature = pow(hash, keyPair.d, keyPair.n)
    #signatures.append(signature)
    if i % 10 ==0:
        print("[+] {}: {}".format(i, time.time()-start))
    
'''
counter=1 
start=time.time()
for s in signatures:
    hash_plum = int.from_bytes(sha512(msg).digest(), byteorder='big')
    hashFromSignature = pow(signature, keyPair.e, keyPair.n)
    if counter % 10 == 0 :
        cost.append(time.time()-start)
    counter+=1

counter=1
for t in cost:
    print("[+] {}: {}".format(counter*10, t))
    counter+=1
'''
