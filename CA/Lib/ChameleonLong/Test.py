from Participator import Participator
from Verifier import Verifier

ver = Verifier()
Px = int(ver.P.x)
Py = int(ver.P.y)

vKx, vKy = ver.get_Kn()
msg = 'Hello'
vr = ver.Signing(msg)

part = Participator(Px, Py, ver.k, ver.q)

#print('ch: ', ver.CHash == part.CHash)
result = part.Verifying(msg, vr, vKx, vKy)

print(result)