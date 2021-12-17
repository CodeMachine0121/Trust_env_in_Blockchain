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
    #print(clientPub)

    # Px,Py,k,q,Knx,Kny     
    #en_k = rsa.EncryptFunc(str(ver.k), clientPub)
    # encrypt k in fucture
        

    return HttpResponse(
        json.dumps({
            'k': ver.k,
            'Knx':ver.Kn.x,
            'Kny':ver.Kn.y,
        }),
        content_type='application/json'
    )




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


## AG 申請註冊 要確認得到的k是否正確
def AG_Register(request):
    # TK key 透過其他管道進行傳輸
    print(request.body)
    upload = json.loads(request.body.decode("utf-8"))
    ## 請對於訊息進行加密
    msg = upload.get('msg')
    Knx = upload.get('Knx')
    Kny = upload.get('Kny')
    signature = upload.get('signature')

    result = ver.Verifying(msg, signature, Knx, Kny)

    return HttpResponse(result)
