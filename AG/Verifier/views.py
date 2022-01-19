from django.shortcuts import render
from django.http import HttpResponse
import json
import sys
import requests
from .Logic.ChameleonShort.Verifier import Verifier
from .Logic.RSA.rsa import RSA_Library
from .Logic.longMiddleware import longMiddleware
from .Logic.Blockchain.UseContract import RecordContract
from .Logic.Blockchain.UseContract import TransactionContract

# 變色龍雜湊
rsa = RSA_Library()
lpart = longMiddleware()
sver = Verifier(lpart.CA_k)

## Blockchain
RContract = RecordContract()
TContract = TransactionContract()



# API Function
## Register_for_Clients
def get_shortTerm_SystemParameters(request):
    return HttpResponse(json.dumps({
        "Px": int(sver.P.x),
        "Py": int(sver.P.y),
        "q": sver.q,
        "Knx": int(sver.Kn.x),
        "Kny": int(sver.Kn.y),
        "RSA_PublicKey": rsa.OutputPublic()}), content_type='application/json')


# Session key 交換 採用 ECDH
def sessionKey_exchange(request):
    # 我覺得需要公鑰去記得誰的Session Key是哪一把
    # 接收另一半 zP.x zP.y
    # 回傳 x^{-1} * P
    # 在此階段將Client紀錄在智能合約中

    data = json.loads(request.body.decode("utf-8"))
    xpX, xpY = sver.start_SessionKey()

    zpX = data.get('zpX')
    zpY = data.get('zpY')
    KnX = data.get("KnX")
    address = data.get("address")
    
    print("[+] New session key exchanging: {}".format(address))
    print("[+] Adding Client to Record Contract list")
    
    RContract.registerClient(address)

    sver.set_SessionKey(zpX, zpY, KnX, address)  # 這邊就會初始化變色龍雜湊

    return HttpResponse(json.dumps({"xPX": xpX, "xPY": xpY}), content_type="application/json")


## 執行 Client 的指令前要做的事情
def short_Receiver_Actions(data):
    # use rsa algorithm to en/decrypt message
    # cipher will present as hex string
    print("[+] Decryptign message")
    msg = rsa.DecryptFunc(data.get('msg'))
    print("[+] Get message: {}".format(msg))
    r_plum = data.get('r')
    Knx = data.get("Knx")
    Kny = data.get("Kny")
    
    # rsa public key
    cliPublic = data.get('RSA_publicKey')
    address = data.get('chainAddress')
    result = sver.Verifying(msg, r_plum, Knx, Kny, address)

    print("[*] Initialize Result: {}".format(result))

    return result    

## 查詢使用者是否在此AG管轄範圍
def find_Client_available(request):
    data = json.loads(request.body.decode("utf-8"))
    if not short_Receiver_Actions(data):
        return HttpResponse('Authentication Failed', status=401)

    result = data.get('Target_address') in list(sver.sessionKeys.keys())
    return HttpResponse(str(result), status=200)

## 使用者要求離開AG管轄範圍
def quit_this_AG(request):
    data = json.loads(request.body.decode('utf-8'))
    if not short_Receiver_Actions(data):
        return HttpResponse('Authentication Failed', status=401)
    # 字典內刪除該項目
    del sver.sessionKeys[data.get('chainAddress')]
    return HttpResponse('Done', status=200) 

## 遞送交易訊息
def Make_Transaction(request):
    data = json.loads(request.body.decode('utf-8'))
    if not short_Receiver_Actions(data):
        return HttpResponse("Authentication Failed", status=401)

    print("[+] Receive Transaction requests from: ", data["from"])

    # get transaction data
    from_addr = data["from"]
    to_addr =  data["to"]
    balance = data["balance"]
   
   # 要透過 To_addr 取找他所屬的AG的位址
    toAG = RContract.findAGviaAddress(to_addr)
    

    # 交易結果
    result = True
    return HttpResponse(result, status=200)


