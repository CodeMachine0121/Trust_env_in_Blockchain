from django.shortcuts import render
from django.http import HttpResponse
import json
import sys
from web3 import Web3
from Logic.LongTermCode import LongTermCode as LPart
from Logic.ShortTermCode import ShortTermCode as SVer

# 變色龍雜湊
lpart = LPart()
sver = SVer(lpart.Px, lpart.Py, lpart.q, lpart.kn, lpart.k)
# --------------------------------------------------------- #
# 乙太坊區塊鏈網路


NodeHost = "https://192.168.0.135:8545"
w3 = Web3(Web3.HTTPProvider(NodeHost))
Txn_List = {}  ## 存放交易雜湊用的字典


# API Function
## Register_for_Clients
def getSystem_Parameters(request):
    return HttpResponse(json.dumps({
        "Px": sver.Px,
        "Py": sver.Py,
        "q": sver.q,
        "Knx": int(sver.sver.Kn.x),
        "Kny": int(sver.sver.Kn.y)}), content_type='application/json')


# Session key 交換 採用 ECDH
def SessionKey_exchange(request):
    # 我覺得需要公鑰去記得誰的Session Key是哪一把
    # 接收另一半 zP.x zP.y
    # 回傳 x^{-1} * P
    data = json.loads(request.body.decode("utf-8"))
    xpX, xpY = sver.SessionKey()
    zpX = data.get('zpX')
    zpY = data.get('zpY')
    sver.setSessionKey(zpX, zpY)

    return HttpResponse(json.dumps({"xpX": xpX, "xpY": xpY}), content_type="application/json")


## 簽名驗證
def Verify_ChameleonHash(request):
    # 應該收到 m,r,Kn
    data = json.loads(request.body.decode("utf-8"))
    m = data.get('msg')
    r = data.get('r')
    Kn = data.get("Kn")

    result = ver.Verifying(m, r, Kn)
    print("[*] Result: {}".format(result))

    return HttpResponse(json.dumps({"result": result}), content_type="application/json")


## 接收交易
def Upload_Transaction(request):
    return


# Local Function (沒有放在API的Function)
## 檢查連線
def Check_Connection():
    return w3.isConnected()


## 取得餘額
def get_Balance(address):
    try:
        if Check_Connection():
            return w3.eth.getBalance(Web3.toChecksumAddress(address))
    except:
        return "Address Error"


## 提出交易
def send_RawTransaction(signed_transaction):
    try:
        txn = w3.eth.send_raw_transaction(signed_transaction)
        transaction = w3.eth.getTransaction(txn)
        return transaction
    except:
        return "Sending Transaction Error"
