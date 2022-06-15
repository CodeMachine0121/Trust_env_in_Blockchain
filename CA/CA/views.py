from django.http import HttpResponse
import json

"""

CA's code

"""
# 變色龍雜湊
from .Lib.ChameleonLong.Verifier import Verifier
from .Lib.RSA.rsa import RSA_Library
from .Lib.Blockchain.DeployContract import RecordContract, TransactionContract

## 變色龍相關宣告
ver = Verifier()

## 區塊練相關宣告
Rcontract = RecordContract()
Tcontract = TransactionContract()

## RSA 加密
rsa = RSA_Library()


# API Function
## Register_for_Clients
def getSystem_Parameters(request):
    # Using rsa to encrypt data
    ## 在RSA加密Func已經實作公鑰的字串轉物件
    clientPub = json.loads(request.body.decode())['PublicKey']
    # print(clientPub)

    # Px,Py,k,q,Knx,Kny     
    # en_k = rsa.EncryptFunc(str(ver.k), clientPub)
    # encrypt k in fucture

    return HttpResponse(
        json.dumps({
            'k': ver.k,
            'Knx': ver.Kn.x,
            'Kny': ver.Kn.y,
        }),
        content_type='application/json'
    )


## AG 申請註冊 要確認得到的k是否正確
def AG_Register(request):
    print("[+] AG Register Phase")
    # TK key 透過其他管道進行傳輸
    upload = json.loads(request.body.decode("utf-8"))
    ## 請對於訊息進行加密
    msg = upload.get('msg')
    Knx = upload.get('Knx')
    Kny = upload.get('Kny')
    signature = upload.get('signature')

    result = ver.Verifying(msg, signature, Knx, Kny)

    print("\t[-] Verify Message: ", msg)
    print("\t[-] AG's Public key x: ", Knx)
    print("\t[-] AG's Public key y: ", Kny)
    print("\t[-] Signature: ", signature)
    print("\t[-] Verify Result: ", result)
    return HttpResponse(result)


## Blockchain Function
### 由CA部屬紀錄合約
### AG需要向CA註冊成為AG 
### 接收每個client的註冊請求

def registerAG_for_RecordContract(request):
    # 向RecordContract合約註冊AG
    postData = json.loads(request.body.decode())

    print("[+] Recording AG[{}] to RecordContract".format(postData['Address']))

    Knx = postData["Knx"]
    Kny = postData["Kny"]
    Rcontract.registerAG(postData['Address'], postData['Domain'], Knx, Kny)

    JData = json.dumps({
        'address': Rcontract.contractAddress,
        'abi': Rcontract.abi
    })
    return HttpResponse(JData, content_type='application/json')


### 由CA部屬交易合約，再交由給AG
### CA 部屬合約後要去判定那些AGs負責
def deployTransactionContract(request):
    # 交易合約
    jsonData = json.loads(request.body.decode())
    address = jsonData['address']
    nonce = Rcontract.nonce

    contractAddress, abi = Tcontract.deploy(address, nonce)
    if abi == None:  # 此時contractAddress 會是異常訊息
        return HttpResponse(contractAddress, status=501)
    else:
        Rcontract.nonce += 1

    return HttpResponse(json.dumps({
        'address': contractAddress,
        "abi": abi,
        "result": True
    }), status=200)


### 取得合約的位址跟ABI
def getTransactionContract(request):
    # 交易合約
    print("[+] Importing Transaction Contract")
    jsonData = json.loads(request.body.decode())
    address = jsonData["address"]

    abi = Tcontract.contractList[address]['abi']
    address = Tcontract.contractList[address]["address"]

    return HttpResponse(
        json.dumps({
            'abi': abi,
            'address': address
        }),
        content_type='application/json'
    )


### 其他AN要與主AN進行註冊
def AN_Register(request):
    print("[+] Receiver AN Register Requests")
    jsonData = json.loads(request.body.decode())
    address = jsonData["address"]

    txn = Rcontract.registerAN(address)
    return HttpResponse(json.dumps({'txn': txn}), content_type="application/json")
