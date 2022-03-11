from django.shortcuts import render
from django.http import HttpResponse
from Crypto.Random.random import getrandbits
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
RContract = RecordContract(sver.Kn.x, sver.Kn.y)

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
        "RSA_PublicKey": rsa.OutputPublic(),
        "Address": TContract.address}), content_type='application/json')


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
    
    # Client 已經註冊過了
    if address in sver.sessionKeys.keys():
        print("[!] Address has already registered")
        return HttpResponse(json.dumps({"xPx":-1, "xPY":-1, 'address': TContract.address}), content_type='application/json')


    print("[+] New session key exchanging: {}".format(address))
    print("[+] Adding Client to Record Contract list")
    
    # 向合約登記此client在他的管轄內
    TContract.setBalanceRecord(address)
    sver.set_SessionKey(zpX, zpY, KnX, address)  # 這邊就會初始化變色龍雜湊
    result = RContract.registerClient(address, sver.sessionKeys[address]["Chash"])


    return HttpResponse(json.dumps({"xPX": xpX, "xPY": xpY, "address":TContract.address}), content_type="application/json")


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

    print("[+] Initialize Result: {}".format(result))

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
    print("[+] Deleting account: [{}]".format(data.get("chainAddress")))
    del sver.sessionKeys[data.get('chainAddress')]
    # 刪除紀錄合約上的紀錄
    RContract.removeClient(data.get("chainAddress"))
    return HttpResponse('Done', status=200) 


## 遞送交易訊息
def createTransaction(request):
    data = json.loads(request.body.decode('utf-8'))
    if not short_Receiver_Actions(data):
        return HttpResponse("Authentication Failed", status=401)

    # show ip of requesters
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print("[+] Receive Transaction requests from: {}".format(ip))
    

    # get transaction data
    from_addr = RContract.web3.toChecksumAddress(data["from_address"])
    to_addr =  RContract.web3.toChecksumAddress(data["to_address"])
    balance = data["balance"]

    # AG對交易訊息簽章
    #seed = int(getrandbits(256)) # 在未來可以加入隨機種子
    msg = str(from_addr)+str(to_addr)+str(balance)
    r = sver.Signing(msg, from_addr)

   # 要透過 To_addr 取找他所屬的AG的位址
    toAG = RContract.findAGviaAddress(to_addr)
    print("[+] toAG: ", toAG)
    if toAG == int("0",16):
        print("[!] Receiver AG is not ready, please try again.")
        return HttpResponse("Receiver AG is not ready, please try again", status=401)

    try:
        txn = TContract.createTransaction(from_addr, to_addr, toAG, balance, r, data["txnHash"] , RContract.nonce)
        RContract.nonce += 1
        r = sver.Signing(txn.hex(), from_addr)
        txnCH = TContract.doAfterTransaction(to_addr,r,RContract.nonce)
        RContract.nonce+=1
    except Exception as e:
        print("[!] Creating Transaction Failed: [{}]".format(repr(e)))
        return HttpResponse("Creating Transaction Failed", status=401)
    # 開啟交易通道結果
    return HttpResponse(json.dumps({"txn":txn.hex(),"txnCH":txnCH.hex()}), status=200)


## 轉帳
def makePayment(request):
    data = json.loads(request.body.decode('utf-8'))
    if not short_Receiver_Actions(data):
        return HttpResponse("Authentication Failed", status=401)

    # show ip of requesters
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR') 
    print("[+] Receive Payment requests from: ".format(ip))

    from_addr = RContract.web3.toChecksumAddress(data["from_address"])
    to_addr =  RContract.web3.toChecksumAddress(data["to_address"])
    balance = data["balance"]

    # 對交易訊息做簽章
    msg = str(from_addr)+str(to_addr)+str(balance+TContract.balanceRecord[from_addr][to_addr].currentAmount)

    r = sver.Signing(msg, from_addr)

    # 要透過 To_addr 取找他所屬的AG的位址
    toAG = RContract.findAGviaAddress(to_addr)
    if toAG == "0":
        return HttpResponse("AG of receiver is not ready") 
   
    try:
        res = TContract.Payment(from_addr, to_addr, toAG, balance, r, RContract.nonce)
        RContract.nonce += 1
        
        
    except Exception as e:
        print("[!] Erroe occured: [{}]".format(repr(e)))
        return HttpResponse("Payment Error",status=401)

    return HttpResponse(res, status=200)

    
def getContractBalance(request):
    # show ip of requesters
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR') 
    print("[+] Receive Balance requests from: {}".format(ip))


    Jdata = json.loads(request.body.decode("utf-8"))
    fromAddr = Jdata["fromAddr"]
    toAddr = Jdata["toAddr"]

    contractAmount, agAmount = TContract.getContractBalance(fromAddr, toAddr)
    data = json.dumps({
        "contractAmount":contractAmount,
        "agAmount": agAmount
        })
    
    return  HttpResponse(data, content_type='application/json', status=200)
 

# 取得發送發AG的TC資訊
def setSenderAG_Contract(request):
    data = json.loads(request.body.decode('utf-8'))
    if not short_Receiver_Actions(data):
        return HttpResponse("Authentication Failed", status=401)
    # 發送方的address 
    from_address = data["from_address"]
    try:
        # 找尋這個Client的AG
        agAddress = RContract.findAGviaAddress(from_address)
        TContract.setSenderAG_Contract(agAddress)
        return HttpResponse(json.dumps({"agAddress":agAddress}), status=200)
    except Exception as e:
        print("[!] getSenderAG_Contract occured problem: [{}]".format(repr(e)))
        return HttpResponse(False, status=401)

# 取得合約
def getTContract(request):
    print("[+] Asking for TC address")
    data = json.loads(request.body.decode('utf-8'))
    if not short_Receiver_Actions(data):
        return HttpResponse(False, content_type='application/json')

    fromAG = data["fromAG"]
    print("\t[-] TC: {}".format(fromAG))
    data = json.dumps({
        "tcAddress": TContract.TCList[fromAG]
    })
    return HttpResponse(data, content_type='application/json', status=200)

# 取得任一AG的公鑰
def getPubKeyFromRContract(request):
    print("[+] Getting Public Key of AG")
    data = json.loads(request.body.decode('utf-8'))

    pubKey = RContract.getAGPublicKey(data["agAddress"])

    data = {
        "x": pubKey[0],
        "y": pubKey[1]
    }
    print("\t[-] ", data)
    return HttpResponse(json.dumps(data), content_type='application/json', status=200)

# 取得該特定AG跟client的short-tern變色龍雜湊值
def getChameleonHash(request):
    print("[+] Getting Chameleon Hash of AG")
    clientAddr = json.loads(request.body.decode("utf-8"))["clientAddr"]
    agAddr = json.loads(request.body.decode("utf-8"))["agAddr"]

    
    CHash = RContract.getChameleonHash(agAddr, clientAddr)
    data = json.dumps({
        "HashX": CHash[0],
        "HashY": CHash[1]
    })
    print("\t[-] ", data)
    return HttpResponse(data, content_type='application/json', status=200)


# 取得交易歷史紀錄(自己的)
def getTransactionHistory(request):
    print("[+] Getting Transaction History")
    data = json.loads(request.body.decode("utf-8"))
    fromAddr = data["fromAddr"]
    toAddr = data["toAdd"]
    return HttpResponse(TContract.getTransactionHistory(fromAddr, toAddr), content_type='application/json', status=200)

def getTransactionHistory_Others(request):
    print("[+] Getting Transaction From other AG")
    data = json.loads(request.body.decode("utf-8"))
    fromAddr = data["fromAddr"]
    toAddr = data["toAddr"]
    fromAG = data["fromAG"]

    # 取得Domain
    print("\t[-] Get Domain of [{}]".format(fromAG))
    domain = RContract.getDomain(fromAG)

    # 取得該AG的交易紀錄
    if domain != RContract.Domain:
        uri = "http://{}/AG/TransactionHistory/".format(domain)
        res = requests.post(uri, data=json.dumps({
            "fromAddr":fromAddr,
            "toAddr":toAddr}
        )).text
    else:
        res = TContract.getTransactionHistory(fromAddr, toAddr)
    return HttpResponse(res, content_type='application/json', status=200)


