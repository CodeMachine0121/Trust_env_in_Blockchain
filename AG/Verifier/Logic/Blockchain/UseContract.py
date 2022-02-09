from web3 import Web3
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
    path = './Verifier/Logic/Blockchain/keystore/'
    for file in os.listdir(path):
        keystore_path = os.path.join(path, file)
        
    with open(keystore_path) as file:
        encrypted_key = file.read()
        private_key = web3.eth.account.decrypt(encrypted_key,'mcuite')
    
    return private_key


# 交易物件
class Transaction():
    def __init__(self):
        self.totalAmount=0
        self.currentAmount = 0



class RecordContract:
    def __init__(self):
        #
        self.CAHost, self.blockchain_address = getServerAddress()
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        
        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3))
        self.address = self.acct.address
        
        self.Domain = "This is AG1"
        self.contract= self.setContract(self.Domain)
        
        self.nonce = self.web3.eth.getTransactionCount(self.address)

        return 
    

    def setContract(self, Domain):
        # set contract
        # 也會同步向CA註冊合約上的AG
        print("[+] Setting Record Contract.....")
        print("[+] Registering to CA ")
        
        API = "{}RecordContract/".format(self.CAHost)
        
        JData = json.dumps({
            'Address': self.address,
            'Domain': self.Domain
            })
        # 註冊RecordContract 並索取合約資訊
        res =requests.post(API, data=JData)
        JData = json.loads(res.text)
        abi = JData['abi']
        address = JData['address']
        

        return self.web3.eth.contract(address = address, abi=abi)
    

    
    def  registerClient(self, cli_address): 
        # 登記註冊的Client
        print("[+] Client [{}] register to RecordContract".format(cli_address))
        try:
            txn = self.contract.functions.registerClient(cli_address).transact({
                'from':self.address,
                #'gasPrice': self.web3.eth.gasPrice,
                'nonce': self.nonce
                })
            self.web3.eth.wait_for_transaction_receipt(txn)
            self.nonce+=1
            return True
        except:
            return False

    def findAGviaAddress(self, cli_address):
        # 透過client address 搜尋  AG位址
        agAddr = self.contract.functions.findAGviaAddress(cli_address).call()
        if int(agAddr,16) == 0:
            print("[!] [{}] have no AG, please try again.".format(cli_address))
            return 0

        print("[+] Find AG of : [{}]".format(cli_address))
        print("\t[-] AG: [{}]".format(agAddr))
        return agAddr

    def removeClient(self, cli_address):
        # 移除已註冊過的Client
        print("[+] Removing Cleint: [{}]".format(cli_address))
        try:
            self.contract.functions.removeClient(cli_address).transact({
                "from": self.address,
                "nonce": self.nonce
                })
            self.nonce+=1
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
        return 
    
    
    def setBalanceRecord(self, cliAddr):
        # Client 註冊時啟動
        self.balanceRecord[cliAddr] = dict()

    def ask_for_DeployContraction(self):
        # 要求ca開啟合約給ag
        print("[+] Asking for contract deployment:")
        API = self.CAHost+"TxnDeploy/"
        res = requests.post(API, data=json.dumps({
                "address": self.address
            }))
        Jres = json.loads(res.text)
        print('\t[-] Result: {}'.format(Jres['result']))

        # 實作合約並加入合約表中
        self.contractABI = Jres["abi"]
        self.contractAddress = Jres["address"]
        return res.text

       
    def createTransaction(self, fromAddr, toAddr, toAG, balance, r, nonce):
        # 開啟交易
        if self.contractABI==None or self.contractAddress==None:
            print( "[!] Contract is not available")
            return False
        if not fromAddr in self.balanceRecord.keys():
            print("[!] Client [{}] has not registered".format(fromAddr))
            return False

        print("[+] Create new Transaction to Tcontract:")
        print("\t[-] Sender: {}".format(fromAddr))
        print("\t[-] Receiver: {}".format(toAddr))
        print("\t[-] Balance: {}".format(balance))
        print("\t [-] Signature: {}".format(r))
       
        self.balanceRecord[fromAddr][toAddr] = Transaction() # 初始化交易物件

        contract = self.web3.eth.contract(abi=self.contractABI, address = self.contractAddress)
        contract.functions.createTransaction(fromAddr, toAddr, toAG, balance, r).transact({
            'from':self.address,
            'nonce':nonce
            })
        
        return True

    
    def Payment(self, fromAddr, toAddr, toAG, balance, r, nonce):  
        # 單次扣款
        if self.contractABI == None or self.contractAddress ==None:   
            print( "[!] Contract is not available")
            return False

        print("[+] Adding new Payment to Tcontract: ")
        print("\t[-] Sender: {}".format(fromAddr))
        print("\t[-] Receiver: {}".format(toAddr))
        print("\t[-] Balance: {}".format(balance))
        print("\t [-] Signature: {}".format(r))

        contract = self.web3.eth.contract(abi=self.contractABI, address=self.contractAddress)
        contract.functions.makePayment(fromAddr, toAddr, toAG, balance, r).transact({
            'from':self.address,
            'nonce': nonce
            })
        
        return True

    

    def getContractBalance(self, fromAddr, toAddr):
        # 取得合約上餘額
        if self.contractABI == None or self.contractAddress == None:
            print("[!] Contract is no available")
            return False

        print("[+] Getting the balanc of the contract")
        print("\t[-] Sender: {}".format(fromAddr))
        print("\t[-] Receiver: {}".format(toAddr))

        contract = self.web3.eth.contract(
                abi = self.contractABI,
                address = self.contractAddress
        )

        totalAmount = contract.functions.getTotalAmount(fromAddr,toAddr).call()
        currentAmount = contract.functions.getCurrentAmount(fromAddr, toAddr).call()

        print("\t[-] totalAmount: {}".format(totalAmount))
        print("\t[-] currentAmount: {}".format(currentAmount))

        return totalAmount, currentAmount
    
    # 取得自己的交易合約資訊
    def getContract(self):
        return self.contractABI, self.contractAddress
    


    # 關閉合約
    def  endContract(self,from_address, to_address):
         # send request to CA
        API = self.CAHost+"/EndContract"
        res = requests.post(API,data=json.dumps({
            'fromAddress': from_address,
            'toAddress': to_address
            }))
        print("[+] Contract has been destroyed")

        return 
