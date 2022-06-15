from web3 import Web3
# from web3.middleware import geth_poa_middleware
import requests
import json
import os


def getServerAddress():
    # 設定 Blockchain Node server
    path = './Verifier/Logic/Blockchain/server.json'
    with open(path) as file:
        JData = json.loads(file.read())
    return JData['CAHost'], JData['NodeServer']


def getKey(web3):
    # 取得區塊鏈金鑰
    keystore_path = ""
    path = './Verifier/Logic/Blockchain/keystore/'
    for file in os.listdir(path):
        keystore_path = os.path.join(path, file)

    with open(keystore_path) as file:
        encrypted_key = file.read()
        private_key = web3.eth.account.decrypt(encrypted_key, 'mcuite')

    return private_key


class RecordContract:
    def __init__(self, Knx, Kny):
        #
        self.CAHost, self.blockchain_address = getServerAddress()
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))

        # self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3))
        self.address = self.web3.toChecksumAddress(self.acct.address)

        self.Domain = "127.0.0.1:8888"
        self.contractAddress = ""
        self.contractABI = ""
        self.contract = self.setContract(Knx, Kny)

        self.nonce = self.web3.eth.getTransactionCount(self.address)

        return

    def setContract(self, Knx, Kny):
        # set contract
        # 也會同步向CA註冊合約上的AG
        print("[+] Setting Record Contract.....")

        API = "{}RecordContract/".format(self.CAHost)
        JData = json.dumps({
            'Address': self.address,
            'Domain': self.Domain,
            "Knx": Knx,
            "Kny": Kny
        })
        # 註冊RecordContract 並索取合約資訊
        res = requests.post(API, data=JData)
        JData = json.loads(res.text)
        self.contractABI = JData['abi']
        self.contractAddress = JData['address']

        return self.web3.eth.contract(address=self.contractAddress, abi=self.contractABI)

    def registerClient(self, cli_address, CHash):
        # 登記註冊的Client
        print("[+] Client [{}] register to RecordContract".format(cli_address))
        try:
            txn = self.contract.functions.registerClient(cli_address, CHash.x, CHash.y).transact({
                'from': self.address,
                # 'gasPrice': self.web3.eth.gasPrice,
                'nonce': self.nonce
            })

            self.web3.eth.wait_for_transaction_receipt(txn)
            self.nonce += 1
            return True
        except Exception as e:
            print("[!] {}".format(repr(e)))
            return False

    def findAGviaAddress(self, cli_address):
        # 透過client address 搜尋  AG位址
        contract = self.web3.eth.contract(abi=self.contractABI, address=self.contractAddress)
        agAddr = contract.functions.findAGviaAddress(cli_address).call()
        if int(agAddr, 16) == 0:
            print("[!] [{}] have no AG, please try again.".format(cli_address))
            return 0

        print("[+] Find AG of : [{}]".format(cli_address))
        print("\t[-] AG: [{}]".format(agAddr))
        return self.web3.toChecksumAddress(agAddr)

    def getAGPublicKey(self, ag_address):
        # 透過AG address尋找對應的公鑰
        publicKey = self.contract.functions.getAGPublicKey(ag_address).call()
        return publicKey

    def getChameleonHash(self, ag_address, Client_address):
        # 透過AG address, client address尋找對應的變色龍雜湊
        chash = self.contract.functions.getClientCHameleonHash(ag_address, Client_address).call()
        return chash

    def getDomain(self, ag_address):
        domain = self.contract.functions.getDomain(ag_address).call()
        return domain

    def removeClient(self, cli_address):
        # 移除已註冊過的Client
        print("[+] Removing Cleint: [{}]".format(cli_address))
        try:
            self.contract.functions.removeClient(cli_address).transact({
                "from": self.address,
                "nonce": self.nonce
            })
            self.nonce += 1
            return True
        except Exception as e:
            print("[!] Erroe occurred: {}".format(repr(e)))
            return False


class TransactionContract:
    def __init__(self):
        #
        self.CAHost, self.blockchain_address = getServerAddress()
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))

        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3))
        self.address = self.web3.toChecksumAddress(self.acct.address)

        self.contractABI = None
        self.contractAddress = None

        self.ask_for_DeployContraction()

        self.balanceRecord = dict()
        self.TCList = dict()
        return

    def setBalanceRecord(self, cliAddr):
        # Client 註冊時啟動
        self.balanceRecord[cliAddr] = dict()

    def ask_for_DeployContraction(self):
        # 要求ca開啟合約給ag
        print("[+] Waiting for TC deployment: ")
        API = self.CAHost + "TxnDeploy/"
        res = requests.post(API, data=json.dumps({
            "address": self.address
        }))
        Jres = json.loads(res.text)
        print('\t[-] Result: {}'.format(Jres['result']))

        # 實作合約並加入合約表中
        self.contractABI = Jres["abi"]
        self.contractAddress = Jres["address"]
        return res.text

    def doAfterTransaction(self, to, r, nonce, status):
        # 每次對合約做完交易的動作就把該交易雜湊值做變色龍發布新交易
        txn = {
            'chainId': 602602,
            'to': to,
            'nonce': nonce,
            'data': str(hex(r)),  ##  欄位會是 input
            'gas': 200000,
            'gasPrice': self.web3.eth.gasPrice,
        }
        signed_tx = self.acct.sign_transaction(txn)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print("[+] Create <signatureTransaction> Transaction txn: ", tx_hash.hex())

        if status == 0:
            self.web3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_hash

    def createTransaction(self, fromAddr, toAddr, toAG, balance, r, nonce):
        # 開啟交易
        if self.contractABI == None or self.contractAddress == None:
            print("[!] Contract is not available")
            return False
        if not fromAddr in self.balanceRecord.keys():
            print("[!] Client [{}] has not registered".format(fromAddr))
            return False

        print("[+] Create new Transaction to Tcontract:")
        print("\t[-] Sender: {}/{}".format(fromAddr, type(fromAddr)))
        print("\t[-] Receiver: {}/{}".format(toAddr, type(toAddr)))
        print("\t[-] Balance: {}/{}".format(balance, type(balance)))
        print("\t[-] Signature: {}/{}".format(r, type(r)))

        self.balanceRecord[fromAddr][toAddr] = Transaction(balance)  # 初始化交易物件

        contract = self.web3.eth.contract(abi=self.contractABI, address=self.contractAddress)
        txn = contract.functions.createTransaction(fromAddr, toAddr, toAG, balance, r).transact({
            'from': self.address,
            'nonce': nonce,
            'value': balance,
        })
        print("[+] Create <createTransaction> Transaction txn: ", txn.hex())
        # 簽章雜湊值 在 views.py 做
        return txn

    def Payment(self, fromAddr, toAddr, toAG, balance, r, nonce):
        # 單次扣款
        if self.contractABI == None or self.contractAddress == None:
            print("[!] Contract is not available")
            return False
        if not fromAddr in self.balanceRecord.keys():
            print("[!] Client [{}] has not registered".format(fromAddr))
            return False
        if balance > self.balanceRecord[fromAddr][toAddr].totalAmount:
            print("[!] Balance: ", balance)
            print("[!] Record : ", self.balanceRecord[fromAddr][toAddr].totalAmount)
            print("[!] Payment value cannot greater than total Amount!")
            return False

        print("[+] Adding new Payment to Tcontract: ")
        print("\t[-] Sender: {}".format(fromAddr))
        print("\t[-] Receiver: {}".format(toAddr))
        print("\t[-] Balance: {}".format(balance))
        print("\t [-] Signature: {}".format(hex(r)))

        # 紀錄交易
        self.balanceRecord[fromAddr][toAddr].setPayment(balance)
        self.balanceRecord[fromAddr][toAddr].setRecord()
        # 實作合約物件
        ## txn: 合約發出的交易雜湊值
        contract = self.web3.eth.contract(abi=self.contractABI, address=self.contractAddress)
        txn = contract.functions.makePayment(fromAddr, toAddr, toAG, balance, r).transact({
            'from': self.address,
            'nonce': nonce
        })
        print("[+] Create <Payment> Transaction txn ", txn.hex())

        return txn, hex(r)

    def getContractBalance(self, fromAddr, toAddr):
        # 取得合約上餘額
        if self.contractABI == None or self.contractAddress == None:
            print("[!] Contract is no available")
            return False
        if not fromAddr in self.balanceRecord.keys():
            print("[!] Client [{}] has not registered".format(fromAddr))
            return False

        print("[+] Getting the balanc")
        print("\t[+] Record on contract")
        print("\t[-] Sender: {}".format(fromAddr))
        contract = self.web3.eth.contract(
            abi=self.contractABI,
            address=self.contractAddress
        )

        print("[-] Receiver: {}".format(toAddr))
        totalAmount = contract.functions.getTotalAmount(fromAddr, toAddr).call()
        currentAmount = contract.functions.getCurrentAmount(fromAddr, toAddr).call()
        contractBalance = (totalAmount, currentAmount)
        print("\t[-] totalAmount: {}".format(totalAmount))
        print("\t[-] currentAmount: {}".format(currentAmount))
        print("##################################")

        print("[+] Getting the balance from the AG record")
        totalAmount = self.balanceRecord[fromAddr][toAddr].totalAmount
        currentAmount = self.balanceRecord[fromAddr][toAddr].currentAmount
        agBalance = (totalAmount, currentAmount)
        print("\t[-] totalAmount: {}".format(self.balanceRecord[fromAddr][toAddr].totalAmount))
        print("\t[-] currentAmount: {}".format(self.balanceRecord[fromAddr][toAddr].currentAmount))

        return contractBalance, agBalance

    # 取得自己的交易合約資訊
    def getContract(self):
        return self.contractABI, self.contractAddress

    # 取得發送方的交易合約
    def setSenderAG_Contract(self, agAddress):
        if agAddress in self.TCList.keys():
            print("[!] AG address is already in the list")
            return False

        # address為from的address
        API = self.CAHost + "TxnContract/"
        res = requests.post(API, data=json.dumps({
            "address": agAddress
        }))

        rdata = json.loads(res.text)

        # 存放此TC的資訊 發送方AG:TC
        self.TCList[agAddress] = rdata["address"]
        return True

    # 取得交易歷史紀錄
    def getTransactionHistory(self, fromAddr, toAddr):
        tran = self.balanceRecord[fromAddr][toAddr]
        history = tran.history  ## list(dict())

        data = dict()
        for i in range(0, len(history)):
            data[i] = history[i]

        return json.dumps(data)
