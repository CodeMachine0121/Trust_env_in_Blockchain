from web3 import Web3, middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
import json
import os


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

class RecordContract:
    def __init__(self):
        self.blockchain_address = getChainNodeAddress()
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        self.acct = self.web3.eth.account.privateKeyToAccount(getKey(self.web3)) 
        # 紀錄交易次數
        self.nonce = self.web3.eth.getTransactionCount(self.acct.address)
        self.contractAddress, self.abi = self.deploy()

        self.contract = self.web3.eth.contract(abi=self.abi,address=self.contractAddress)
        

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
            """
                實驗記錄用 額外儲存ABI
            """ 
            with open("./RABI", 'w') as file:
                file.write(str(contract_json["abi"]))
                file.close()

            return contractAddress, contract_json['abi']
        except IndexError:
            print("[!] Balance is not enough")
        except Exception as e:
            print("[!] other error occurred:\n\t{}".format(repr(e)))
        


        return
    


    def registerAG(self, agAddress, domain):
        self.contract.functions.registerAG(agAddress, domain).transact({'from':self.acct.address})
        
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
        return 
   

    def getContract_data(self):
        compiled_contract_path = './Lib/Blockchain/build/contracts/TransferContract.json'
        with open(compiled_contract_path) as file:
            contract_json = json.loads(file.read())
            # contract_abi = contract_josn['abi']
        return contract_json




    def deploy(self,fromAG, toAG, from_address, to_address, r, nonce):

        print("[+] Deploying TransactionContract ...")
        print("[+] account's address: {}".format(self.acct.address))       
        contract_json = self.getContract_data()

        # 統一格式
        fromAG = self.web3.toChecksumAddress(fromAG)
        toAG = self.web3.toChecksumAddress(toAG)
        from_address = self.web3.toChecksumAddress(from_address)
        to_address = self.web3.toChecksumAddress(to_address)

        
        print("[+] account's nonce: {}".format(nonce))
        contract_ = self.web3.eth.contract(
                abi=contract_json['abi'],
                bytecode=contract_json['bytecode']
        )
        contractConstruct = contract_.constructor(fromAG, toAG, from_address, to_address)

        txn_body = {
            'from': self.acct.address,
            'gas': contractConstruct.estimateGas(),
            'gasPrice': self.web3.eth.gasPrice,
            'nonce': nonce,
        }
        



        # throw IndexError if balance is out of band
        try:
            construct_txn = contractConstruct.transact(txn_body)
            #signed = self.acct.signTransaction(construct_txn)
            #tx_hash = self.web3.toHex(self.web3.keccak(signed.rawTransaction))
            #self.web3.eth.sendRawTransaction(signed.rawTransaction)
            print("[+] Deploy Transaction contract for sender: [{}]".format(from_address))
            
            tx_recipt = self.web3.eth.wait_for_transaction_receipt(construct_txn)
            contractAddress = tx_recipt["contractAddress"]
            #print("[+] contract deploy transaction Hash: [{}]".format(tx_hash))
            print("[+] contract address: [{}]".format(contractAddress))
            return contractAddress, contract_json['abi']

        except IndexError:
            print("[!] Balance is not enough")
        except Exception as e:
            print("[!] other error occurred:\n\t{}".format(repr(e)))
        
        return 






