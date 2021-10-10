from Participator import Participator
from Verifier import Verifier


ver = Verifier()

cpx = int(ver.P.x)
cpy = int(ver.P.y)
HK = ver.Y
q = ver.q

part = Participator(cpx, cpy, q, HK)

### Session key
ver_HalfKey = ver.Session_key_Exchange()
part_HalfKey = part.Session_key_Exchange(ver_HalfKey)
ver.set_Session_key(part_HalfKey)

result = ver.sk == part.sk

msg_v = "message"
r_v = ver.Signing(msg_v)
K_v = ver.Kn

msg_p = "hello"
r_p = part.Signing(msg_p)
K_p = part.Kn

result2 = part.CHash == ver.CHash

result3 = part.Veriying(msg_v, r_v, K_v)
result4 = ver.Verifying(msg_p, r_p, K_p)

print()