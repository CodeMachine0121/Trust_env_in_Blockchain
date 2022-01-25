from django.shortcuts import render
from django.http import HttpResponse
import json
import sys
"""

CA's code

"""
# 變色龍雜湊
sys.path.append('..')
from Lib.ChameleonLong.Verifier import Verifier
from Lib.RSA.rsa import RSA_Library
from Lib.Blockchain.UseContract import usingTransactionsContract
from Lib.Blockchain.DeployContract import RecordContract

## 變色龍相關宣告
ver = Verifier()

## 區塊練相關宣告
Tcontract = usingTransactionsContract()
Rcontract = RecordContract()


## RSA 加密
rsa = RSA_Library()



# API Function
## Register_for_Clients
def getSystem_Parameters(request) :
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


## Blockchain Function
### 由CA部屬紀錄合約
### AG需要向CA註冊成為AG 
### 接收每個client的註冊請求

def registerAG_for_RecordContract(request):
    # 向RecordContract合約註冊AG
    postData = json.loads(request.body.decode())
    
    print("[+] Recording AG[{}] to RecordContract".format(postData['Address'])) 
    Rcontract.registerAG(postData['Address'], postData['Domain'])
    
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
    from_address = jsonData['fromAddress']
    to_address = jsonData['toAddress']
    balance = jsonData['balance']
    AG1 = jsonData['AG1Address']
    AG2 = jsonData['AG2Address']

    # 部屬合約
    print("[+] Deploying Transaction Contract for AG:[{}] ".format(AG1))
    # msg: from+to+AG1+AG2
    msg = str(from_address)+str(to_address)+str(AG1)+str(AG2)
    r = ver.Signing(msg)
    result = Tcontract.deployContract(AG1, AG2, from_address, to_address, r, Rcontract.nonce)
    
    if not result:
        print("[!] Deploy Transaction Contract Failed")
        return HttpResponse(str(False))
    else:
        Rcontract.nonce+=1


   
    # 開啟交易
    print("[+] Creating Transaction Channel")
    r = ver.Signing(from_address+to_address+str(balance))
    result = Tcontract.createTransaction(AG1,from_address, to_address, balance, r, Rcontract.nonce)
    
    if result:
        Rcontract.nonce+=1
    
    return HttpResponse( json.dumps({
            'abi': Tcontract.contractList[AG1][from_address][to_address].abi,
            'contractAddress':Tcontract.contractList[AG1][from_address][to_address].address,
           'result': result,
           "r": r
        }), content_type='application/json' )





### 取得合約的位址跟ABI
def getTransactionContract(request): 
  # 交易合約
    print("[+] Importing Transaction Contract")
    jsonData = json.loads(request.body.decode())
    from_address = jsonData["fromAddress"]
    to_address = jsonData["toAddress"]
    
    abi = Tcontract.contractList[from_address][to_address].abi
    address = Tcontract.contractList[from_address][to_address].address


    return HttpResponse(
        json.dumps({
            'abi': abi,
            'address': address
        }),
        content_type='application/json'
    )

### 結束合約
def closeTransactionContract(request):
    # 交易合約
    jsonData = json.loads(request.body.decode())    
    from_address = jsonData['fromAddress']
    to_address = jsonData['toAddress']
    ag_address = jsonData['agAddress']
    Tcontract.endContract(ag_address, from_address, to_address, Rcontract.nonce)
    Rcontract.nonce+=1
    return HttpResponse("Contract has been destroyed")
###   


