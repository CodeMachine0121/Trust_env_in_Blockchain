from web3 import Web3, middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
import json
import os
import requests

def getKey(web3):
    # privatekey hard code problem
    path="./Lib/Blockchain/keystore"
    for file in os.listdir(path):
        keystore_path = os.path.join(path, file)
        
    with open(keystore_path) as file:
        encrypted_key = file.read()
        private_key = web3.eth.account.decrypt(encrypted_key, 'mcuite')
    return  private_key

def getChainNodeAddress():
    with open("./Lib/Blockchain/server.json") as file:
        JData = json.loads(file.read())
    return JData["nodeAddress"]

def requestAN(address):
    res = requests.post("http://192.168.50.136:8000/AN_Register/", data=json.dumps({"address":address}))
    txn = json.loads(res.text)["txn"]
    return txn


class RecordContract:
    def __init__(self):
        self.blockchain_address = getChainNodeAddress()
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3)) 
        # 紀錄交易次數
        self.nonce = self.web3.eth.getTransactionCount(self.acct.address)
        
        ## 是否要套入RC合約
        try:
            status = int(input("Whether import RC (0 or 1): "))
        except:
            status = 0
        
        if status ==0:
            self.contractAddress, self.abi = self.deploy()
        elif status ==1:
            self.contractAddress = self.web3.toChecksumAddress(input("RC Address: "))
            self.abi = self.getContract_data()["abi"]
            requestAN(self.acct.address)

        self.contract = self.web3.eth.contract(abi=self.abi,address=self.contractAddress)
        
    def registerAN(self, anAddress, ):
        txn = self.contract.functions.registerAN(anAddress).transact({"from":self.acct.address, "nonce":self.nonce})
        self.nonce+=1
        return txn.hex()

    def getContract_data(self):
        compiled_contract_path = './Lib/Blockchain/build/contracts/RecordContract.json'
        with open(compiled_contract_path) as file:
            contract_json = json.loads(file.read())
        return contract_json
    

    def deploy(self):
        print("[+] Deploying RecordContract ...")
        print("[+] deployer's address: {}".format(self.acct.address))       
        contract_json = self.getContract_data()
        
        
        print("[+] account's nonce: {}".format(self.nonce))
        contract_ = self.web3.eth.contract(
                abi=contract_json['abi'],
                bytecode=contract_json['bytecode']
        )

        txn_body = {
            'from': self.acct.address,
            #'gas': 300000,
            'gasPrice': self.web3.eth.gasPrice,
            'nonce': self.nonce
        }
        
        self.nonce += 1

        construct_txn = contract_.constructor().buildTransaction(txn_body)
        signed = self.acct.signTransaction(construct_txn)
        tx_hash = self.web3.toHex(self.web3.keccak(signed.rawTransaction))

        # throw IndexError if balance is out of band
        try:
            self.web3.eth.sendRawTransaction(signed.rawTransaction)
            print("[+] RecordContract txn: [{}]".format(tx_hash))
            
            tx_recipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            contractAddress = tx_recipt.contractAddress
            print("[+] contract deploy transaction Hash: [{}]".format(tx_hash))
            print("[+] RecordContract address: [{}]".format(contractAddress))
            return contractAddress, contract_json['abi']

        except Exception as e:
            print("[!] other error occurred:\n\t{}".format(repr(e)))

        return
    


    def registerAG(self, agAddress, domain, Knx, Kny):
        self.contract.functions.registerAG(agAddress, domain, Knx, Kny).transact({'from':self.acct.address, 'nonce':self.nonce})
        
        self.nonce+=1
        return 
    

class TransactionContract:  
    def __init__(self):
        """
            由於Record會優先被使用，所以 nonce就由Record物件紀錄
        """
        self.blockchain_address = getChainNodeAddress()
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        #self.web3.eth.set_gas_price_strategy(fast_gas_price_strategy)
 #       self.web3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        self.web3.eth.set_gas_price_strategy(medium_gas_price_strategy)

        self.web3.middleware_onion.add(middleware.time_based_cache_middleware) 
        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3))
        self.contractList = dict()
        return 
   
    # 取得合約 abi, bytecode
    def getContractData(self):
        with open("./Lib/Blockchain/build/contracts/TransferContract.json") as file:
            Jdata =  json.loads(file.read())
        
        abi = Jdata["abi"]
        bytecode = Jdata["bytecode"]
        return abi, bytecode

    def deploy(self,fromAG, nonce):

        print("[+] Deploying TransactionContract ...")
        print("[+] account's address: {}".format(self.acct.address))       
        abi, bytecode = self.getContractData()

        # 統一格式
        fromAG = self.web3.toChecksumAddress(fromAG)

        # throw IndexError if balance is out of band
        
        try:

            print("[+] account's nonce: {}".format(nonce))
            contractConstruct = self.web3.eth.contract(
                abi=abi,
                bytecode=str(bytecode)
            ).constructor(self.web3.eth.coinbase, fromAG)
            

            txn_body = {
                'from': self.acct.address,
                'gas': contractConstruct.estimateGas(),
                'gasPrice': self.web3.eth.gasPrice,
                'nonce': nonce}
            result = contractConstruct.transact(txn_body)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(result)

            # store the contract information
            self.contractList[fromAG]=dict()
            self.contractList[fromAG]["abi"] = abi
            self.contractList[fromAG]["address"] = tx_receipt.contractAddress

            contractAddress = tx_receipt.contractAddress
            print("[+] contract address: [{}]".format(contractAddress))
            print("[+] Deploy contract test: ")
            contract = self.web3.eth.contract(address=contractAddress, abi=abi)
            print("\t[-] CA: [{}]".format(contract.functions.getCA().call()))
            print("\t[-] Owner: [{}]".format(contract.functions.getOwner().call()))
            
            return contractAddress , abi

        except IndexError as e:
            print("[!] Error occurred: {}".format(repr(e)))
            return repr(e), None
        except Exception as e:
            print("[!] other error occurred:\n\t{}".format(repr(e)))
            return repr(e), None
