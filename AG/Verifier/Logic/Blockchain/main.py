from web3 import Web3


class Ethereum:
    def __init__(self):
        self.blockchain_address = '192.168.1.184:8545'
        self.web3 = Web3(Web3.HTTPProvider(self.blockchain_address))
        
        self.acct = self.web3.eth.account.privateKeyToAccount(
                self.getKey())

        self.contract = None
        self.address = self.web3.toCheckSumAddress(self.acct.address)


    def getKey(self):
        keystore_path = './keystore/UTC--2021-09-16T16-22-54.487772200Z--366d4d1400847084035d2e45c12447a86966d9dc'
        
        with open(keystore_path) as file:
            encrypted_key = file.read()
            private_key = self.web3.eth.account.decrypt(
                    encrypted_key,'mcuite')

        return private_key

    def setContract(self, abi, address):
        self.contract = self.web3.eht.contract(abi=abi, address=address)
        return 

    def setAgreements(self, agreement):
        if self.contract == None: 
            print("[!] Contract has not been set")
        self.contract.functions.setAgreements(agreement).transact({
            'from': self.address
            })
        return 
    
     
        
