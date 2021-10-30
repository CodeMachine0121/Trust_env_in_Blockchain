from django.shortcuts import render
from django.http import HttpResponse
import json
import sys

# 變色龍雜湊
sys.path.append('..')
from Lib.ChameleonLong.Verifier import Verifier

## 變色龍相關宣告
ver = Verifier()

## 區塊練相關宣告
Contract_addr = ""
Contract_abi = ""


# API Function
## Register_for_Clients
def getSystem_Parameters(request):
    return HttpResponse(
        # ZP, x_plum, k, q, HK, CHash
        json.dumps({
            "Px": int(ver.P.x),
            "Py": int(ver.P.y),
            "k": ver.k,
            "q": ver.q,
            "Knx": int(ver.Kn.x),
            "Kny": int(ver.Kn.y),
        }),
        content_type='application/json'
    )


### AG 會來要求變色龍雜湊
def get_Chameleon_Hash(request):
    return HttpResponse(json.dumps({'result': ver.CHash}),
                        content_type='application/json')


## Client 會來要求給合約簽章
def get_Contract_Certificate(request):
    r = ver.Signing(Contract_addr + Contract_abi)
    return HttpResponse(json.dumps(
        {
            'signature': r,
            'Address': Contract_addr,
            'ABI': Contract_abi
        }
    ), content_type='application/json')


## AG 申請註冊
def AG_Register(request):
    # TK key 透過其他管道進行傳輸
    upload = json.loads(request.body.decode("utf-8"))
    ## 請對於訊息進行加密
    msg = upload.get('msg')
    Kn = upload.get('Kn')
    signature = upload.get('signature')

    result = ver.Verifying(msg, signature, Kn)

    return HttpResponse(json.dumps({'result': result}))
