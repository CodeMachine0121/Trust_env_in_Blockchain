from web3 import Web3
import requests
import json


class ContractStructure:
    def __init__(self, abi, address, from_address, to_address, balance):
        self.abi = abi
        self.address = address
        self.from_address = from_address
        self.to_address = to_address
        self.balance = balance

class TransactionContract:
    def __init__(self):
        #
        self.CAHost = 'http://140.125.32.10:8000/'
        self.blockchain_address = self.getNodeAddr()
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        
        #self.acct = self.web3.eth.account.privateKeyToAccount(
         #       self.getKey())
        #self.address = self.web3.toChecksumAddress(self.acct.address)
        self.address = self.web3.eth.accounts[0]
        self.contractList = dict()
        

    def getKey(self):
        #
        keystore_path = './keystore/UTC--2021-09-16T16-22-54.487772200Z--366d4d1400847084035d2e45c12447a86966d9dc'
        
        with open(keystore_path) as file:
            encrypted_key = file.read()
            private_key = self.web3.eth.account.decrypt(
                    encrypted_key,'mcuite')

        return private_key

    def getNodeAddr(self): 
        # 設定 Blockchain Node server
        path = './server'
        with open(path) as file:
            server = file.read().strip(" ")
        return server

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
        print("[+] Seeting Contract: to:[{}]".format(to_address))
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
