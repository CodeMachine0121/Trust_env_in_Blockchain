from django.shortcuts import render
from django.http import HttpResponse
import json
import sys

# 變色龍雜湊
sys.path.append('..')
from Lib.ChameleonLong.Verifier import Verifier
from Lib.RSA.rsa import RSA_Library


## 變色龍相關宣告
ver = Verifier()

## 區塊練相關宣告
Contract_addr = ""
Contract_abi = ""

## RSA 加密
rsa = RSA_Library()



# API Function
## Register_for_Clients
def getSystem_Parameters(request):
# only AG
    # Using rsa to encrypt data
    ## 在RSA加密Func已經實作公鑰的字串轉物件
    clientPub = json.loads(request.body.decode())['PublicKey']
    
    # Px,Py,k,q,Knx,Kny 
    
    en_Px = rsa.EncryptFunc(str(int(ver.P.x)), clientPub)
    en_Py = rsa.EncryptFunc(str(int(ver.P.y)), clientPub)
    
    en_k = rsa.EncryptFunc(str(ver.k), clientPub)
    en_q = rsa.EncryptFunc(str(ver.q), clientPub)

    en_Knx = rsa.EncryptFunc(str(int(ver.Kn.x)), clientPub)
    en_Kny = rsa.EncryptFunc(str(int(ver.Kn.y)), clientPub)
        


    return HttpResponse(
        json.dumps({
            'Px': en_Px.hex(),
            'Py': en_Py.hex(),
            'k': en_k.hex(),
            'q': en_q.hex(),
            'Knx':en_Knx.hex(),
            'Kny':en_Kny.hex(),
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
    Knx = upload.get('Knx')
    Kny = upload.get('Kny')
    signature = upload.get('signature')

    result = ver.Verifying(msg, signature, Knx, Kny)

    return HttpResponse(json.dumps({'result': result}))
