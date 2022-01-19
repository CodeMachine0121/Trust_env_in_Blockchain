from django.test import TestCase
import json
import sys
# 變色龍雜湊
sys.path.append('..')
from Lib.ChameleonLong.Participator import Participator as LongPart
from Lib.ChameleonLong.Verifier import Verifier as LongVer

from Lib.ChameleonShort.Participator import Participator as ShortPart
from Lib.ChameleonShort.Verifier import Verifier as ShortVer



# Create your tests here.
tmp = 0
for i in range(0,100):
    LV = LongVer()
    LP = LongPart(int(LV.P.x), int(LV.P.y), LV.k, LV.q)

    msg = "Jelly"
    r = LV.Signing(msg)
    result = LP.Verifying(msg, r, int(LV.Kn.x), int(LV.Kn.y))

    msg = "Hello"
    r = LP.Signing(msg)
    result2 = LV.Verifying(msg, r, int(LP.Kn.x), int(LP.Kn.y))



    # 短期變色龍
    SV = ShortVer(int(LV.P.x), int(LV.P.y), LV.q, LV.kn, LV.k)
    SP = ShortPart(int(SV.P.x), int(SV.P.y), SV.q)

    # Session key
    xpX, xpY = SV.Session_key_Exchange()
    zpX, zpY = SP.Session_key_Exchange(xpX, xpY)
    SV.set_Session_key(zpX, zpY)


    msg = "JJJJ"
    r = SV.Signing(msg)
    result3 = SP.Verifying(msg, r, int(SV.Kn.x), int(SV.Kn.y))


    msg = "GGGGG"
    r = SP.Signing(msg)
    result4 = SV.Verifying(msg, r, int(SP.Kn.x), int(SP.Kn.y))

    if result and result2 and result3 and result4:
        tmp += 1

print(tmp)
print()