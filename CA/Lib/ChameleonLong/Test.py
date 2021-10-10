from Participator import Participator
from Verifier import Verifier

ver = Verifier()


cpk = int(ver.k)
czp = ver.ZP
cpx_plum = ver.x_plum
cpq = ver.q
HK = ver.Y
CHash = ver.CHash

part = Participator(czp, cpx_plum, cpk, cpq, HK, CHash)


vmsg = 'you'
pmsg = 'me'
vr = ver.Signing(vmsg)
pr = part.Signing(pmsg)

result = ver.Verifying(pmsg, pr, part.Kn)
result2 = part.Veriying(vmsg, vr, ver.Kn)

print()