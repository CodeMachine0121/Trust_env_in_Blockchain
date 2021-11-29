from django.shortcuts import render
from django.http import HttpResponse
import json
import sys

from .Logic.LongTermCode import LongTermCode as LPart
from .Logic.ChameleonShort.Verifier import Verifier as SVer
from .Logic.RSA.rsa improt RSA_Library
# 變色龍雜湊
lpart = LPart()
sver = SVer()
rsa = RSA_Library()

# --------------------------------------------------------- #


# API Function
## Register_for_Clients
def get_shortTerm_SystemParameters(request):
    return HttpResponse(json.dumps({
        "Px": int(sver.P.x),
        "Py": int(sver.P.y),
        "q": sver.q,
        "Knx": int(sver.Kn.x),
        "Kny": int(sver.Kn.y)}), content_type='application/json')


# Session key 交換 採用 ECDH
def sessionKey_exchange(request):
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


## 接收執行 Client 的指令
def short_Receiver_Actions(request):
    """
        參數:{
            encrypted_msg
            Knx, Kny
            r_plum
            Client PublicKey
        }
        輸出: 指令結果(加密)
    """
    # use rsa algorithm to en/decrypt message
    # cipher will present as hex string 
    data = json.loads(request.body.decode("utf-8"))
    msg = rsa.DecryptFunc(bytes.fromhex(data.get('msg')))
    r_plum = data.get('r')
    Knx = data.get("Knx")
    Kny = data.get("Kny")
    
    # rsa public key
    cliPublic = data.get('publicKey')

    result = sver.VerifySignature(msg, r_plum, Knx, Kny)

    print("[*] Result: {}".format(result))

    
    # 加密訊息
    m = rsa.EncryptFunc("return", cliPublic)  # 依照上面的指令做完後的回傳直
    r = sver.MakeSignature(m, Knx)

    return HttpResponse(
        json.dumps(
            {
                "result": result,
                "signature": r,
                "msg": m
            }), content_type="application/json")

# Local Function (沒有放在API的Function)
