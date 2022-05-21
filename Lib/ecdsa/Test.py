from ellipticcurve import Ecdsa, PrivateKey, Signature
import time

# Generate Keys
privateKey = PrivateKey()
publicKey = privateKey.publicKey()

message = "My test message"


# Generate Signature

cost = []
start= time.time()
for i in range(1,101):
    signature = Ecdsa.sign(message, privateKey)
    if i % 10 ==0:
        cost.append(time.time()-start)

#Ecdsa.verify(message, signatures[i], publicKey)
counter = 1
for t in cost:
    print("[+] {}: {}".format((counter+1)*10, t))

# Verify if signature is valid
