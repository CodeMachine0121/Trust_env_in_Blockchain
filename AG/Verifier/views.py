from django.shortcuts import render
from django.http import HttpResponse
import json
import sys

# 變色龍雜湊
sys.path.append('..')
from Lib.Chameleon.Verifier import Verifier
from Lib.Chameleon.Participator import Participator

## Create your views here.
ver = Verifier()
P = ver.P
q = ver.q
HK = ver.Y
Kn = ver.Kn
x_plum = ver.x_plum

# --------------------------------------------------------- #
# 乙太坊區塊鏈網路
from web3 import Web3

NodeHost = "https://192.168.0.135:8545"
w3 = Web3(Web3.HTTPProvider(NodeHost))
Txn_List = {}  ## 存放交易雜湊用的字典


# API Function
## Register_for_Clients
def getSystem_Parameters(request):
    return HttpResponse(json.dumps({"P": P, "q": q, "Kn": Kn, "HK": HK, "x_plum": x_plum}),
                        content_type='application/json')


# Session key 交換 採用 ECDH
def SessionKey_exchange(request):
    # 計算 P*k
    Pk = P * ver.k
    zP = json.loads(request.body.decode("utf-8")).get('zP')
    ver.sk = zP * ver.k

    rv = ver.Signing("Init SK")
    return HttpResponse(json.dumps({"Pk": Pk}), content_type="application/json")


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
