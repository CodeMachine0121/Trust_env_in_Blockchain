from web3 import Web3
from web3.gas_strategies.time_based import fast_gas_price_strategy
from DeployContract import TransactionContract



class Contract:
    '''
        calling
            contract.functions.<functionName>().call()
    '''
    def __init__(self):
        # get contract object
        self.deploy = TransactionContract()
        self.address = self.deploy.web3.toChecksumAddress(self.deploy.acct.address)
        ## how to control deploy or not
        #self.contract_address, abi = self.deploy.deploy()
        self.isContractDeploy = False
        self.contract_address = ""
        self.contract = None
        #self.contract = self.deploy.web3.eth.contract(abi = abi, address = self.contract_address)
       
        return 

    def deployContract(self,):
        self.contract_address,abi =  self.deploy.deploy()
        self.isContractDeploy=True
        try:
            self.contract = self.deploy.web3.eth.contract(abi = abi, address = self.contract_address)
        except ConnectionError:
            self.isContractDeploy = False
            print("[!] Connection refused")
        return ;


    def getAGs(self,):
        if not self.isContractDeploy:
            print("Contract hasn't been deployed'")
            return None
        address = self.contract.functions.getAGs().call()
        return address


    def setAG(self, AG1_address, AG2_address):
        if not self.isContractDeploy:
            print("Contract hasn't been deployed'")
            return None

        AG1_address = self.deploy.web3.toChecksumAddress(AG1_address)
        AG2_address = self.deploy.web3.toChecksumAddress(AG2_address)

        self.contract.functions.setAGs(AG1_address,AG2_address).transact({'from':self.address})
        return
    

    def createTransaction(self,fromAddr, toAddr, balance, signature):
        if not self.isContractDeploy:
            print("Contract hasn't been deployed'")
            return None

        fromAddr = self.deploy.web3.toChecksumAddress(fromAddr)
        toAddr = self.deploy.web3.toChecksumAddress(toAddr)
        self.contract.functions.createTransaction(fromAddr, toAddr, balance, signature).transact({'from':self.address})
        return 

    def endContract(self, ):
        if not self.isContractDeploy:
            print("Contract hasn't been deployed'")
            return None

        self.contract.functions.endContract().transact({'from':self.address})
