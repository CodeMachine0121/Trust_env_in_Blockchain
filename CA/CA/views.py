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
from Lib.Blockchain.UseContract import Contract
from Lib.Blockchain.DeployContract import RecordContract

## 變色龍相關宣告
ver = Verifier()

## 區塊練相關宣告
contract = Contract()
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
    
    # 像合約註冊AG
    postData = json.loads(request.body.decode())

    Rcontract.registerAG(postData['Address'], postData['Domain'])
    
    JData = json.dumps({
        'address': Rcontract.contractAddress,
        'abi': Rcontract.abi
        })
    return HttpResponse(JData, content_type='application/json')



### 由CA部屬交易合約，再交由給AG
### CA 部屬合約後要去判定那些AGs負責
def deployContract(request):
# 交易合約
    jsonData = json.loads(request.body.decode())
    from_address = jsonData['fromAddress']
    to_address = jsonData['toAddress']
    AG1 = jsonData['AG1Address']
    AG2 = jsonData['AG2Address']

    # 部屬合約
    contract.deployContract(from_address, to_address)
    contract.setAG(from_address,to_address, AG1,AG2)

    return HttpResponse("Deploy Contract Successfully")


### 確定好雙方AG的同意後就可以開啟交易
def  open_TransactionChannel(request):
# 交易合約
    jsonData = json.loads(request.body.decode())
    from_address = jsonData["fromAddress"]
    to_address = jsonData["toAddress"]
    balance = jsonData["balance"]
    
    # 計算合約簽章
    r = ver.Signing(from_address+ to_address+ str(balance))
    # 開啟交易通道
    contract.createTransaction(from_address, to_address, balance,r)
    
    return HttpResponse("Transaction channel open successfully")




### 取得合約的位址跟ABI
def getContract(request):
  # 交易合約
    jsonData = json.loads(request.body.decode())
    from_address = jsonData["fromAddress"]
    to_address = jsonData["toAddress"]
    
    abi = contract.contractList[from_address][to_address].abi
    address = contract.contractList[from_address][to_address].address


    return HttpResponse(
        json.dumps({
            'abi': abi,
            'address': address
        }),
        content_type='application/json'
    )

### 結束合約
def closeContract(request):
    # 交易合約
    jsonData = json.loads(request.body.decode())    
    from_address = jsonData['fromAddress']
    to_address = jsonData['toAddress']
    contract.endContract(from_address, to_address)
    return HttpResponse("Contract has been destroyed")
###   


