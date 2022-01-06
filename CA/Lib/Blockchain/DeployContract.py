from web3 import Web3
from web3.gas_strategies.time_based import fast_gas_price_strategy
import json

class DeployContract:  
    def __init__(self):
        self.blockchain_address = 'http://140.125.32.10:8545'
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        self.web3.eth.set_gas_price_strategy(fast_gas_price_strategy)
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        return 
   


    def getContract_data(self):   
        compiled_contract_path = 'build/contract/TransferContract.json'
        with open(compiled_contract_path) as file:
            contract_json = json.loads(file.read())
            # contract_abi = contract_josn['abi']
        return contract_json



    def getKey(self):
        # privatekey hard code problem
        keystore_path = './keystore/UTC--2022-01-06T14-53-08.996835597Z--d4210130bbda22436e58547026f98a6ec17dad22'
        with open(keystore_path) as file:
            encrypted_key = file.read()
            private_key = self.web3.eth.account.decrypt(encrypted_key, 'mcuite')
        return  private_key



    def deploy(self):
       
        contract_json = self.getContract_data()
        private_key = self.getKey()
        

        contract_ = self.web3.eth.contract(
                abi=contract_json['abi'],
                bytecode=contract_json['bytecode']
        )
        
        acct = self.web3.eth.account.privateKeyToAccount(private_key)
        
        construct_txn = contract_.constructor().buildTransaction({
            'from':acct.address,
            'nonce':self.web3.eth.getTransactionCount(acct.address),
        })

        signed = acct.signTransaction(construct_txn)
        tx_hash = self.web3.toHex(self.web3.keccak(signed.rawTransaction))

        # throw IndexError if balance is out of band
        try:
            self.web3.eth.sendRawTransaction(signed.rawTransaction)
            print("[+] Deploy contract: [{}]".format(tx_hash))
            
            tx_recipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            contractAddress = tx_recipt.contractAddress
            print("[+] contract address: [{}]".format(contractAddress))

        except IndexError:
            print("[!] Balance is not enough")
        except Exception as e:
            print("[!] other error occurred:\n\t{}".format(repr(e)))
        
        return contractAddress, contract_json['abi']







