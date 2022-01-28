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
            self.contract.functions.registerClient(cli_address).transact({
                'from':self.address,
                #'gasPrice': self.web3.eth.gasPrice,
                'nonce': self.nonce
                })
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

class TransactionContract:
    def __init__(self):
        #
        self.CAHost, self.blockchain_address = getServerAddress() 
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        
        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3))
        self.address = self.web3.toChecksumAddress(self.acct.address)
        #self.address = self.web3.eth.accounts[0]
        self.contractList = dict()
        
    def addContract(self,abi,contractAddress, from_address, to_address, balance):
        contract = ContractStructure(abi, contractAddress, from_address, to_address, balance)
        if from_address in self.contractList.keys():
            self.contractList[from_address][to_address] = contract
        else:
            self.contractList[from_address] = dict()
            self.contractList[from_address][to_address] = contract

        return 

    def ask_for_DeployContraction(self,AG1, AG2, from_address, to_address, balance):
        # 開啟交易通道
        if from_address in self.contractList.keys():
            if to_address in self.contractList[from_address].keys():
                print("[!] Transaction is already in exist")
                return False


        print("[+] Asking for contract deployment: to[{}] ".format(to_address))
        API = self.CAHost+"TxnDeploy/"
        res = requests.post(API, data=json.dumps({
            'fromAddress': from_address,
            'toAddress': to_address,
            'balance': balance,
            'AG1Address':AG1,
            "AG2Address":AG2,
            }))
        
        Jres = json.loads(res.text)
        print('\t[-] Result: {}'.format(Jres['result']))
        
        # 實作合約並加入合約表中
        self.addContract(Jres['abi'], Jres['contractAddress'], from_address, to_address, balance)
        
        
        return res.text

 
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

    def setAgreements(self,from_address , to_address, agreement, nonce):
       # AG 自行使用 確認是否同意交易
        if not from_address in self.contractList.keys(): 
            print("[!] Contract has not been deployed yet!")
        elif not to_address in self.contractList[from_address].keys():
            print("[!] Contract has not been deployed yet!")
                
        contract = self.web3.eth.contract(
                abi = self.contractList[from_address][to_address].abi,
                address = self.contractList[from_address][to_address].address
                )
        print("[+] Sending agreement to contract: [{}]".format(self.contractList[from_address][to_address].address))
        # agreement = True or False
        try:
            contract.functions.setAgreements(agreement).transact({
                'from': self.address,
                'gasPrice': self.web3.eth.gasPrice,
                'nonce': nonce
                })
            return True
        except Exception as e:
            print("[!] Error occur: [{}]".format(repr(e)))
            
            return False


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


    # 單次付款
    def Payment(self, fromAddr, toAddr, balance, r, nonce):  
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
                fromAddr, toAddr, balance, r).transact({
                    'from': self.address,
                    'gasPrice': self.web3.eth.gasPrice,
                    'nonce': nonce
                    })
            
        return True
    

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
