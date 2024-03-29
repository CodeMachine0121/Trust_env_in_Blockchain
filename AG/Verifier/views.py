from django.http import HttpResponse
import json
from .Logic.Authentication import SmsVerify
from .Logic.ChameleonShort.Verifier import Verifier
from .Logic.ChameleonShort import SessionKeyManagement as SKM

from .Logic.CipherAlgorithm import AES_Library as AESfunc
from .Logic.longMiddleware import longMiddleware
from .Logic.Blockchain.UseContract import RecordContract
from .Logic.Blockchain.UseContract import TransactionContract

# 變色龍雜湊
lpart = longMiddleware()
lpart.Register_to_CA()

sver = Verifier(lpart.CA_k)

## Blockchain
RContract = RecordContract(sver.Kn.x, sver.Kn.y)
TContract = TransactionContract()

## 記錄使用者資訊: address為index
userList = dict()


# API Function
# Register_for_Clients
def get_shortTerm_SystemParameters(request):
    return HttpResponse(json.dumps({
        "Px": int(sver.P.x),
        "Py": int(sver.P.y),
        "q": sver.q,
        "Knx": int(sver.Kn.x),
        "Kny": int(sver.Kn.y),
        "Address": TContract.address}), content_type='application/json')


## 取得短期變色龍簽章公鑰
def get_PublicKey(reqeust):
    data = json.dumps({
        "Knx": int(sver.Kn.x),
        "Kny": int(sver.Kn.y)
    })
    return HttpResponse(data, content_type="application/json")


# 註冊請求
def registerRequest(request):
    data = json.loads(request.body.decode('utf-8'))
    SmsVerify.sendOneTimePassword_SMS(data.get("phoneNumber"))
    print("[+] OPT SMS has already sent to ", data.get("phoneNumber"))
    # 登記client資訊
    userData = {
        "Id": data.get("Id"),
        "Name": data.get("Name"),
        "liveAddress": data.get("liveAddress"),
        "Phone": data.get("phoneNumber"),
        "Email": data.get("email"),
        "chainAddress": data.get("chainAddress"),
    }
    userList[data.get("chainAddress")] = userData
    return HttpResponse(status=200)


# 更新 Session key
def updateSessionKey(request):
    data = json.loads(request.body.decode('utf-8'))
    zpX = data["zpX"]
    zpY = data["zpY"]
    address = data["address"]
    cli_PubX = data["cliPub"]

    if address not in sver.sessionKeys.keys():
        print("[!] Address has not registered yet")
        return HttpResponse(json.dumps(
            {"result": "Address has not registed yet"}), status=401, content_type='application/json')

    client = sver.sessionKeys[address]
    SKM.emptySessionKey(client)

    sver.set_SessionKey(zpX, zpY, userList[address]["otp"], cli_PubX, address)  # 這邊就會初始化變色龍雜湊
    # 這邊就會初始化變色龍雜湊
    result = RContract.registerClient(address, sver.sessionKeys[address]["Chash"])

    xpX, xpY = sver.start_SessionKey()
    return HttpResponse(json.dumps({"xpX": xpX, "xpY": xpY}))


# 重新寄送OTP信件
def reSendOtpSMS(request):
    data = json.loads(request.body.decode('utf-8'))
    SmsVerify.sendOneTimePassword_SMS(data.get("phoneNumber"))
    return HttpResponse(status=200)


# Session key 交換 採用 ECDH
def sessionKey_exchange(request):
    # 我覺得需要公鑰去記得誰的Session Key是哪一把
    # 接收另一半 zP.x zP.y
    # 回傳 x^{-1} * P
    # 在此階段將Client紀錄在智能合約中
    data = json.loads(request.body.decode("utf-8"))
    phoneNumber = data.get("phoneNumber")
    OtpAns = data.get("otpAnswer")
    address = data.get("address")

    # opt Authentication

    if not SmsVerify.verifyOneTimePassword_SMS(phoneNumber, OtpAns):
        print("[!] SMS OTP verified result: Fail")
        return HttpResponse(json.dumps({"result": "OPT Authentication Failed"}),
                            content_type="application/json", status=401)
    else:
        print("[+] SMS OTP verified result: True")

    # session Exchange
    xpX, xpY = sver.start_SessionKey()
    zpX = data.get('zpX')
    zpY = data.get('zpY')
    KnX = data.get("KnX")

    # Client 已經註冊過了
    if address in sver.sessionKeys.keys():
        print("[!] Address has already registered")
        return HttpResponse(json.dumps({"result": "Already registered"}), content_type='application/json')

    print("[+] New session key exchanging: {}".format(address))
    print("[+] Adding Client to Record Contract list")

    # 向合約登記此client在他的管轄內
    TContract.balanceList[address] = dict()
    userList[address]["otp"] = OtpAns
    sver.set_SessionKey(zpX, zpY, OtpAns, KnX, address)  # 這邊就會初始化變色龍雜湊

    result = RContract.registerClient(address, sver.sessionKeys[address]["Chash"])
    if not result:
        return HttpResponse(json.dumps({"result": "Session key Exchange Failed"}),
                            content_type="application/json")

    return HttpResponse(json.dumps({"xPX": xpX, "xPY": xpY, "address": TContract.address}),
                        content_type="application/json")


# 執行 Client 的指令前要做的事情
def short_Receiver_Actions(data):
    # use rsa algorithm to en/decrypt message
    # cipher will present as hex string
    # 在這裡檢測sessionKey 是否過期
    address = data.get('chainAddress')
    result = SKM.ifSessionKey_outDate(sver.sessionKeys[address]['times'])
    if result:
        print("[!] Client's Session Key is Out of Date !!")
        return False, "SessionKey is Out of Date!"

    print("[+] Decrypt the message")
    iv = data.get("iv")
    key = sver.sessionKeys[address]["sk"]
    enmsg = data.get("msg")
    msg = AESfunc.Decrypt(key, enmsg, iv)

    returnData = dict()
    returnData["from_address"] = msg.split(":")[0]
    returnData["to_address"] = msg.split(":")[1]
    returnData["balance"] = msg.split(":")[2]
    # msg = rsa.DecryptFunc(data.get('msg'))
    # data['from_address'] = rsa.DecryptFunc(data.get("from_address"))
    # data['to_address'] = rsa.DecryptFunc(data.get('to_address'))
    # data['balance'] = rsa.DecryptFunc(data.get('balance'))
    print("[+] Get message: {}".format(msg))

    # 簽章驗證
    r_plum = data.get('r')
    Knx = data.get("Knx")
    Kny = data.get("Kny")
    result = sver.Verifying(msg, r_plum, Knx, Kny, address)

    print("[+] Initialize Result: {}".format(result))
    sver.refresh_KeyPair()
    return result, returnData


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
    address = data.get("chainAddress")
    msg = AESfunc.Decrypt(sver.sessionKeys[address]["sk"], data.get("msg"), data.get("iv"))
    result = sver.Verifying(msg, data["r"], data["Knx"], data["Kny"], address)
    if not result:
        return HttpResponse('Authentication Failed', status=401)
    # 字典內刪除該項目
    print("[+] Deleting account: [{}]".format(address))
    del sver.sessionKeys[address]
    # 刪除紀錄合約上的紀錄
    RContract.removeClient(address)
    return HttpResponse('Done', status=200)


## 遞送交易訊息
def createTransaction(request):
    data = json.loads(request.body.decode('utf-8'))
    result, data = short_Receiver_Actions(data)
    if not result:
        return HttpResponse(json.dumps({"result": data}), status=401)

    # show ip of requesters
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print("[+] Receive Transaction requests from: {}".format(ip))

    # get transaction data
    from_addr = RContract.web3.toChecksumAddress(data["from_address"])
    to_addr = RContract.web3.toChecksumAddress(data["to_address"])
    balance = int(data["balance"])

    # AG對交易訊息簽章
    # seed = int(getrandbits(256)) # 在未來可以加入隨機種子
    # 要透過 To_addr 取找他所屬的AG的位址
    toAG = RContract.findAGviaAddress(to_addr)
    print("[+] toAG: ", toAG)
    if toAG == int("0", 16):
        print("[!] Receiver AG is not ready, please try again.")
        return HttpResponse("Receiver AG is not ready, please try again", status=401)

    # AG 自行再針對交易訊息進行簽章
    msg = str(from_addr) + str(to_addr) + str(balance)
    r = sver.Signing(msg, from_addr)

    try:
        txn = TContract.createTransaction(from_addr, to_addr, toAG, balance, r, RContract.nonce)
        r = sver.Signing(txn.hex(), from_addr)
        RContract.nonce += 1  ## 不能直接加2 後面交易會出錯
        txnCH = TContract.doAfterTransaction(to_addr, r, RContract.nonce, 0)
        RContract.nonce += 1
    except Exception as e:
        print("[!] Creating Transaction Failed: [{}]".format(repr(e)))
        return HttpResponse("Creating Transaction Failed", status=401)
    # 開啟交易通道結果
    return HttpResponse(json.dumps({"txn": txn.hex(), "txnCH": txnCH.hex(), 'contractAddr': TContract.address}),
                        status=200)


## 轉帳
def makePayment(request):
    # client透過兩個簽章作為本次扣款的收據

    result, data = short_Receiver_Actions(json.loads(request.body.decode('utf-8')))
    if not result:
        return HttpResponse(json.dumps({"result": data}), status=401)

    # show ip of requesters
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    print("[+] Receive Payment requests from: ".format(ip))

    from_addr = RContract.web3.toChecksumAddress(data["from_address"])
    to_addr = RContract.web3.toChecksumAddress(data["to_address"])
    balance = int(data["balance"])

    # AG 自行再針對交易訊息進行簽章
    msg = str(from_addr) + str(to_addr) + str(balance)
    r = sver.Signing(msg, from_addr)


    # 要透過 To_addr 取找他所屬的AG的位址
    toAG = RContract.findAGviaAddress(to_addr)
    if toAG == "0":
        return HttpResponse("AG of receiver is not ready")

    try:
        txn, paymentSign = TContract.Payment(from_addr, to_addr, toAG, balance, r, RContract.nonce)
        RContract.nonce += 1

        ## 針對合約發出的交易進行變色龍簽章再發送一筆交易出去
        r = sver.Signing(txn.hex(), from_addr)
        txnCH = TContract.doAfterTransaction(to_addr, r, RContract.nonce, 1)
        RContract.nonce += 1

        ### txn: 合約交易 , txnCH: 變色龍簽章
    except Exception as e:
        print("[!] Erroe occured: [{}]".format(repr(e)))
        return HttpResponse("Payment Error", status=401)

    return HttpResponse(json.dumps(
        {"txn": txn.hex(), "txnCH": txnCH.hex(), "contractAddr": TContract.contractAddress, "paymentSign": paymentSign,
         "Address": RContract.address}), status=200)


def getContractBalance(request):
    # show ip of requesters
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    Jdata = json.loads(request.body.decode("utf-8"))
    fromAddr = Jdata["fromAddr"]
    toAddr = Jdata["toAddr"]

    totalAmount, payedAmount = TContract.getContractBalance(fromAddr, toAddr)
    data = json.dumps({
        "totalAmount": totalAmount,
        "payedAmount": payedAmount
    })

    return HttpResponse(data, content_type='application/json', status=200)


# 取得任一AG的公鑰
def getPubKeyFromRContract(request):
    print("[+] Getting Public Key of AG")
    data = json.loads(request.body.decode('utf-8'))

    pubKey = RContract.getAGPublicKey(data["agAddress"])

    data = {
        "x": pubKey[0],
        "y": pubKey[1],
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


## 後續追蹤部分
