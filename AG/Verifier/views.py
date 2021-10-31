from django.shortcuts import render
from django.http import HttpResponse
import json
import sys

from .Logic.LongTermCode import LongTermCode as LPart
from .Logic.ChameleonShort.Verifier import Verifier as SVer

# 變色龍雜湊
lpart = LPart()
sver = SVer()


# --------------------------------------------------------- #


# API Function
## Register_for_Clients
def getSystem_Parameters(request):
    return HttpResponse(json.dumps({
        "Px": int(sver.P.x),
        "Py": int(sver.P.y),
        "q": sver.q,
        "Knx": int(sver.Kn.x),
        "Kny": int(sver.Kn.y)}), content_type='application/json')


# Session key 交換 採用 ECDH
def SessionKey_exchange(request):
    # 我覺得需要公鑰去記得誰的Session Key是哪一把
    # 接收另一半 zP.x zP.y
    # 回傳 x^{-1} * P
    data = json.loads(request.body.decode("utf-8"))
    xpX, xpY = sver.start_SessionKey()

    zpX = data.get('zpX')
    zpY = data.get('zpY')
    KnX = data.get("KnX")
    sver.set_SessionKey(zpX, zpY, KnX)  # 這邊就會初始化變色龍雜湊

    return HttpResponse(json.dumps({"xPX": xpX, "xPY": xpY}), content_type="application/json")


## 簽名驗證
def short_Receiver(request):
    data = json.loads(request.body.decode("utf-8"))
    msg = data.get('msg')
    r_plum = data.get('r')
    Knx = data.get("Knx")
    Kny = data.get("Kny")

    result = sver.VerifySignature(msg, r_plum, Knx, Kny)

    print("[*] Result: {}".format(result))

    m = "return"  # 依照上面的指令做完後的回傳直
    r = sver.MakeSignature(m, Knx)

    return HttpResponse(
        json.dumps(
            {
                "result": result,
                "signature": r,
                "msg": m
            }), content_type="application/json")

# Local Function (沒有放在API的Function)
