from web3 import Web3

# 乙太坊區塊鏈網路
NodeHost = "https://192.168.0.135:8545"
w3 = Web3(Web3.HTTPProvider(NodeHost))
Txn_List = {}  ## 存放交易雜湊用的字典

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
