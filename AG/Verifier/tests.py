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

LV = LongVer()
LP = LongPart(int(LV.P.x), int(LV.P.y), LV.k, LV.q)

msg = "Jelly"
r = LV.Signing(msg)
result = LP.Verifying(msg, r, int(LV.Kn.x), int(LV.Kn.y))

msg = "Hello"
r = LP.Signing(msg)
result2 = LV.Verifying(msg, r, int(LP.Kn.x), int(LP.Kn.y))
print(result2)

# 短期變色龍
SV = ShortVer(int(LV.P.x), int(LV.P.y), LV.q, LV.kn, LV.k)
SP = ShortPart(int(SV.P.x), int(SV.P.y), SV.q)
# Session key


msg = "JJJJ"



