from web3 import Web3
#from web3.gas_strategies.time_based import *
import json

class TransactionContract:  
    def __init__(self):
        self.blockchain_address = 'http://140.125.32.10:8545'
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        #self.web3.eth.set_gas_price_strategy(fast_gas_price_strategy)
 #       self.web3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        
        self.acct = self.web3.eth.account.privateKeyToAccount(self.getKey())
        return 
   

    def getContract_data(self):
        compiled_contract_path = 'build/contracts/TransferContract.json'
        with open(compiled_contract_path) as file:
            contract_json = json.loads(file.read())
            # contract_abi = contract_josn['abi']
        return contract_json



    def getKey(self):
        # privatekey hard code problem
        keystore_path = './keystore/UTC--2021-09-30T16-57-15.509977951Z--69c99ad33abed10c9d4ab7110b39408f9fda2817'
        
        with open(keystore_path) as file:
            encrypted_key = file.read()
            private_key = self.web3.eth.account.decrypt(encrypted_key, 'mcuite')
        return  private_key


    def deploy(self):
        print("[+] address: {}".format(self.acct.address))       
        contract_json = self.getContract_data()
        
        nonce = self.web3.eth.getTransactionCount(self.acct.address) 


        print("[+] nonce: {}".format(nonce))
        contract_ = self.web3.eth.contract(
                abi=contract_json['abi'],
                bytecode=contract_json['bytecode']
        )
        txn_body = {
            'from': self.acct.address,
            'gasPrice': self.web3.eth.gasPrice,
            'nonce': nonce
        }
        


        construct_txn = contract_.constructor().buildTransaction(txn_body)

        signed = self.acct.signTransaction(construct_txn)
        tx_hash = self.web3.toHex(self.web3.keccak(signed.rawTransaction))

        # throw IndexError if balance is out of band
        try:
            self.web3.eth.sendRawTransaction(signed.rawTransaction)
            print("[+] Deploy contract: [{}]".format(tx_hash))
            
            tx_recipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            contractAddress = tx_recipt.contractAddress
            print("[+] contract deploy transaction Hash: [{}]".format(tx_hash))
            print("[+] contract address: [{}]".format(contractAddress))

        except IndexError:
            print("[!] Balance is not enough")
        except Exception as e:
            print("[!] other error occurred:\n\t{}".format(repr(e)))
        


        return contractAddress, contract_json['abi']






