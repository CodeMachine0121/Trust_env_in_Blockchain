import Participator as Pa
import Verifier as Ver
from Crypto.Random.random import getrandbits

ver = Ver.Verifier()

P = ver.P
q = ver.q
HK = ver.Y
x_plum = ver.x_plum

z = int(getrandbits(16))
zP = z * P  # from Client

kP = ver.k * P  # from verifier

# session key
skV = zP * ver.k
skC = kP * z

ver.sk = skV
client = Pa.Participator(P, q, HK, x_plum, skC)

# Verifier create Hash
rv = ver.Signing("server")

# Client Signature
rc = client.Signing("Client")

v_Hash = ver.CHash

c_Hash = client.CHash

result = ver.Verifying("Client", rc, client.Kn)
print()
