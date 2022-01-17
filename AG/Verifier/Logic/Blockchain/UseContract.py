from web3 import Web3
import requests
import json
import os

def getServerAddress():
# 設定 Blockchain Node server
    path = './server'
    with open(path) as file:
        JData = json.loads(file.read())
    return JData['CAHost'], JData['NodeServer']

def getKey(web3):
# 取得區塊鏈金鑰
    for file in os.listdir('keystore'):
        keystore_path = os.path.join('keystore', file)
        
    with open(keystore_path) as file:
        encrypted_key = file.read()
        private_key = web3.eth.account.decrypt(encrypted_key,'mcuite')
    
    return private_key



class ContractStructure:
    def __init__(self, abi, address, from_address, to_address, balance):
        self.abi = abi
        self.address = address
        self.from_address = from_address
        self.to_address = to_address
        self.balance = balance
 


class RecordContract:
    def __init__(self):
        #
        self.CAHost, self.blockchain_address = getServerAddress()
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        
        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3))
        self.address = self.acct
        self.contract= self.setContract()

        return 
    
    def setContract(self):
        # set contract

        print("[+] Setting Record Contract.....")
        API = "{}RecordContract/".format(self.CAHost)

        res =requests.get(API)
        JData = json.loads(res.text)

        abi = JData['abi']
        address = JData['address']
        
        return self.web3.eth.contract(address = address, abi=abi)
         
    
    def  registerClient(self, cli_address):
        # 登記註冊的Client
        self.contract.functions.registerClient(cli_address).transact({'from':self.address})
        return 

    def findAGviaAddress(self, cli_address):
        return self.contract.functions.findAGviaAddress(cli_address)
        

class TransactionContract:
    def __init__(self):
        #
        self.CAHost, self.blockchain_address = getServerAddress() 
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        
        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3))
        self.address = self.web3.toChecksumAddress(self.acct.address)
        #self.address = self.web3.eth.accounts[0]
        self.contractList = dict()
        

   

    def ask_for_DeployContraction(self,AG1, AG2, from_address, to_address):
        #
        print("[+] Asking for contract deployment: to[{}] ".format(to_address))
        API = self.CAHost+"TxnDeploy/"
        res = requests.post(API, data=json.dumps({
            'fromAddress': from_address,
            'toAddress': to_address,
            'AG1Address':AG1,
            "AG2Address":AG2,
            }))
        
        print('[+] {}'.format(res.text))
        return 
        #

    def setContract(self, from_address,  to_address, balance):
        # 建立合約物件，再把他加入合約字典中 
        print("[+] Setting Transaction Contract: to:[{}]".format(to_address))
        API = "{}TxnContract/".format(self.CAHost)

        res = requests.post(API, data= json.dumps({
            'fromAddress': from_address,
            'toAddress': to_address
            }))
        JData = json.loads(res.text)
        abi = JData['abi']
        address = JData['address']

        contract = ContractStructure(abi, address, from_address, to_address, balance)
        
        self.contractList[from_address] = dict()
        self.contractList[from_address][to_address] = contract
        return 

    def setAgreements(self,from_address , to_address, agreement):
       # AG 自行使用 確認是否同意交易
        if not from_address in self.contractList.keys(): 
            print("[!] Contract has not been deployed yet!")
        elif not to_address in self.contractList[from_address].keys():
            print("[!] Contract has not been deployed yet!")
                
        contract = self.web3.eth.contract(
                abi = self.contractList[from_address][to_address].abi,
                address = self.contractList[from_address][to_address].address
                )
        print("Sending agreement to contract: [{}]".format(self.contractList[from_address][to_address].address))
        # agreement = True or False
        
        nonce = self.web3.eth.getTransactionCount(self.address)
        contract.functions.setAgreements(agreement).transact({
            'from': self.address,
            'gasPrice': self.web3.eth.gasPrice,
            'nonce': nonce
            })
        return
    
    def checkStep(self,from_address, to_address):
        #
        if not from_address in self.contractList.keys(): 
            print("[!] Contract has not been deployed yet!")
        elif not to_address in self.contractList[from_address].keys():
            print("[!] Contract has not been deployed yet!")
        
        contract = self.web3.eth.contract(
                abi = self.contractList[from_address][to_address].abi,
                address = self.contractList[from_address][to_address].address
                )

        setp = contract.functions.checkStep().call()
        return setp
        #


    def Payment(self, fromAddr, toAddr, balance):  
        #
        if not fromAddr in self.contractList.keys(): 
            print("[!] Contract has not been deployed yet!")
        elif not toAddr in self.contractList[fromAddr].keys():
            print("[!] Contract has not been deployed yet!")
        
        contract = self.web3.eth.contract(
                abi = self.contractList[fromAddr][toAddr].abi,
                address = self.contractList[fromAddr][toAddr].address
                )

        contract.functions.Payment(
                fromAddr, toAddr, balance).transact({
                    'from': self.address
                    })
        return 





    # 開啟交易通道
    def createTransaction(self,fromAddr, toAddr, balance):
        # calculate signature
        if not fromAddr in self.contractList.keys(): 

            print("[!] Contract has not been deployed yet!")
        elif not toAddr in self.contractList[fromAddr].keys():
            print("[!] Contract has not been deployed yet!")
        
        API = self.CAHost+"NewTxnChannel/"
        # 在CA那邊會計算交易的變色龍雜湊值
        res = requests.post(API, data = json.dumps({
            'fromAddress': fromAddr,
            'toAddress': toAddr,
            'balance': balance
            }))
        if "successfully" not in res.text:
            print("[!] Transaction created failed!")
        return 


    # 關閉合約
    def  endContract(self,from_address, to_address):
         # send request to CA
        if not from_address in self.contractList.keys(): 
            print("[!] Contract has not been deployed yet!")
        elif not to_address in self.contractList[from_address].keys():
            print("[!] Contract has not been deployed yet!")

        API = self.CAHost+"/EndContract"
        res = requests.post(API,data=json.dumps({
            'fromAddress': from_address,
            'toAddress': to_address
            }))
        print("[+] Contract has been destroyed")

        return 
