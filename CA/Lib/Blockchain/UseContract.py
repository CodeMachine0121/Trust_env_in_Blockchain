from web3 import Web3
from .DeployContract import TransactionContract

class ContractStructure:
    def __init__(self, abi, address, from_address,to_address,IsDeployed ):
        self.abi = abi
        self.address = address
        self.from_address = from_address
        self.to_address = to_address
        self.IsDeployed = IsDeployed



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
        self.isDeployed = False
        self.contract_address = ""
        
        # 以發送端位址為 index
        self.contractList = dict()

        return 
    
    def deployContract(self, from_address,to_address):
        if from_address in self.contractList.keys():
            print("[!] Contract is already deployed")

        # 存放合約資料
        contract_address,abi =  self.deploy.deploy()
        
        contract = ContractStructure(abi, contract_address, from_address, to_address, True)

        self.contractList[from_address] =dict()
        self.contractList[from_address][to_address] = contract
        return ;


    def getAGs(self,from_address, to_address):
        if from_address in self.contractList.keys():
            print("[!] Contract is not been created yet")
            return None

        if not self.contractList[from_address].IsDeployed:
            print("[!] Contract hasn't been deployed'")
            return None
        contract = self.deploy.web3.eth.contract(
                adddress=self.contractList[from_address][to_address].address, 
                abi = self.contractList[from_address][to_address].abi)
        

        AG_address = contract.functions.getAGs().call()
        return AG_address

    def setAG(self,from_address,to_address, AG1_address, AG2_address):
        if from_address in self.contractList.keys():
            print("[!] Contract is not been created yet")
            return None


        if not self.contractList[from_address][to_address].IsDeployed:
            print("[!] Contract hasn't been deployed'")
            return None
        
        contract = self.deploy.web3.eth.contract(
                address = self.contractList[from_address][to_address].address,
                abi = self.contractList[from_address][to_address].abi
                )
        
        AG1_address = self.deploy.web3.toChecksumAddress(AG1_address)
        AG2_address = self.deploy.web3.toChecksumAddress(AG2_address)

        contract.functions.setAGs(AG1_address,AG2_address).transact({'from':self.address})
        return
    

    def createTransaction(self,fromAddr, toAddr, balance, signature):
        # fromAddr = from_address
        if not fromAddr in self.contractList.keys():
            print("[!] Contract is not been created yet")
            return None
        if not toAddr in self.contractList[fromAddr].keys():
            print("[!] CContract is not yet created yet")
            return None



        if not self.contractList[fromAddr][toAddr].IsDeployed:
            print("[!] Contract hasn't been deployed'")
            return None
        contract = self.deploy.web3.eth.contract(
                address = self.contractList[fromAddr][toAddr].address,
                abi = self.contractList[fromAddr][toAddr].abi
                )
        fromAddr = self.deploy.web3.toChecksumAddress(fromAddr)
        toAddr = self.deploy.web3.toChecksumAddress(toAddr)
        contract.functions.createTransaction(fromAddr, toAddr, balance, signature).transact({'from':self.address})
        return 

    def endContract(self,from_address, to_address ):
        if from_address in self.contractList.keys():
            print("[!] Contract is not created yet")
            return None
        elif to_address in self.contractList[from_address][to_address].keys():
            print("[!] Contract is not created yet")
            return None
        if not self.contractList[from_address][to_address].IsDeployed:
            print("[!] Contract hasn't been deployed'")
            return None
        contract = self.deploy.web3.eth.contract(
                address= self.contractList[from_address][to_address].address,
                abi = self.contractList[from_address][to_address].abi
                )
        contract.functions.endContract().transact({'from':self.address})

        return
