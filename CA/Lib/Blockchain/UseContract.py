from web3 import Web3
from .DeployContract import TransactionContract


class ContractStructure:
    def __init__(self, abi, address, ag_address ,from_address, to_address, IsDeployed ):
        self.abi = abi
        self.address = address
        self.ag_address = ag_address
        self.from_address = from_address
        self.to_address = to_address
        self.IsDeployed = IsDeployed



class usingTransactionsContract:
    '''
        calling
            contract.functions.<functionName>().call()
    '''
    def __init__(self):
        # get contract object
        self.deploy = TransactionContract()
        ## how to control deploy or not
        #self.contract_address, abi = self.deploy.deploy()
        self.isDeployed = False
        self.contract_address = ""
        
        # 以發送端位址為 index
        self.contractList = dict()
        
        # CA address
        self.address = self.deploy.acct.address
        return 
    
    def getAGs(self, ag_address, from_address, to_address):
        
        try:
            contractobj = self.contractList[ag_address][from_address][to_address]
        except Exception as e:
            print("[!] oether error occureed:\n\t{}".format(repr(e)))
    
        contract = self.deploy.web3.eth.contract(
                adddress= contractobj.address, 
                abi = contractobj.abi)
        

        AG_address = contract.functions.getAGs().call()
        return AG_address




    # CA 設定該份交易合約的兩大AG為何
    def setAG(self,from_address, to_address, AG1_address, AG2_address, nonce):
        print("[+] Setting AG in TransactionContract <setAG>")
        print("\t[-] AG1: [{}]".format(AG1_address))
        print("\t[-] AG2: [{}]".format(AG2_address))

        try:
            AG1_address = self.deploy.web3.toChecksumAddress(AG1_address)
            AG2_address = self.deploy.web3.toChecksumAddress(AG2_address)
         
            contractobj = self.contractList[AG1_address][from_address][to_address ]

            """ 宣告合約物件 """
            contract = self.deploy.web3.eth.contract(
                    address = contractobj.address,
                    abi = contractobj.abi
                )
            contract.functions.setAGs(AG1_address,AG2_address).transact({
                'from':self.address,
                'nonce': nonce
            })
            return True
        
        except Exception as e:
            print("[!] Error occurred: ".format(repr(e)))
            return False

    # CA 發布交易合約
    def deployContract(self, ag_address, from_address,to_address, nonce):
        
        # 確認合約是否已經被部屬過或是未過期
        if ag_address in self.contractList.keys():
            if from_address in self.contractList[ag_address].keys():
                if to_address in self.contractList[ag_address][from_address].keys():
                    print("[!] Contract has been created ")



        # 存放合約資料
        try:
            contract_address,abi =  self.deploy.deploy(nonce)
            

            contract = ContractStructure(abi, contract_address, ag_address ,from_address, to_address, True)
       
            '''
                為了記錄交易合約屬於誰
                以三個索引值作為key: agAddress, fromAddress, toAddress
            '''
            self.contractList[ag_address] = dict()
            self.contractList[ag_address][from_address] =dict()
            self.contractList[ag_address][from_address][to_address] = contract
            
            """
                實驗記錄用: 額外儲存ABI
            """
            with open("./TABI",'w') as file:
                file.write(str(abi))
                file.close()



            return True 
        except Exception as e:
            print("[!] Error Coccurred: {}".format(repr(e)))
            return False

        return True

    # CA 開啟交易通道
    def createTransaction(self, ag_address, from_address, to_address, balance, signature, nonce):
        if not ag_address in self.contractList.keys():
            print("[!] Contract hasn't been created yet(AG) <makeTransaction>")
        elif not from_address in self.contractList[ag_address].keys():
            print("[!] Contract hasn't been created(From) yet <makeTransaction>")
        elif not to_address in self.contractList[ag_address][from_address].keys():
            print("[!] Contract hasn't been created yet(To) <makeTransaction>")
        
        try: 
            contractobj = self.contractList[ag_address][from_address][to_address ]

            contract = self.deploy.web3.eth.contract(
                address = contractobj.address,
                abi = contractobj.abi
                )
        # <要在看對R做甚麼事情>
            contract.functions.createTransaction(from_address, to_address, balance,signature).transact({
                'from': self.address,
                'nonce': nonce
            })
            return True
        
        except Exception as e:
            print("[!] error occurred: {}".format(repr(e)))
            return False



    def endContract(self, ag_address, from_address, to_address, nonce ):
        
        if not ag_address in self.contractList.keys():
            print("[!] Contract hasn't been created yet(AG) <makeTransaction>")
        elif not from_address in self.contractList[ag_address].keys():
            print("[!] Contract hasn't been created(From) yet <makeTransaction>")
        elif not to_address in self.contractList[ag_address][from_address].keys():
            print("[!] Contract hasn't been created yet(To) <makeTransaction>")
        
        contractobj = self.contractList[ag_address][from_address][to_address]
        contract = self.deploy.web3.eth.contract(
                address= contractobj.address,
                abi = contractobj.abi
                )

        contract.functions.endContract().transact({
            'from':self.address,
            'nonce':nonce
            })

        return
