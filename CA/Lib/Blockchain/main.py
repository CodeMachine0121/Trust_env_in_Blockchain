from web3 import Web3

server = '192.168.1.184:8545'
Contract_abi = '[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":false,"inputs":[{"internalType":"uint256","name":"P","type":"uint256"},{"internalType":"uint256","name":"q","type":"uint256"},{"internalType":"uint256","name":"g","type":"uint256"},{"internalType":"string","name":"domain","type":"string"}],"name":"New_an_AG","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"AG_addr","type":"address"}],"name":"Get_AG_Chameleon_Parameters","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"AG_addr","type":"address"}],"name":"Add_Client_to_AG","outputs":[{"internalType":"uint256[]","name":"","type":"uint256[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"Client_addr","type":"address"}],"name":"Finding_AG_with_ClientAddr","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"AG_addr","type":"address"}],"name":"Transfer_to_Smart","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"Receiver_addr","type":"address"}],"name":"Pay_for_Receiver","outputs":[],"payable":true,"stateMutability":"payable","type":"function"}]'
Contract_addr = '0x1925Efb3896089dc821D2f053D12C702206352D3'


class Ethereum:
    def __init__(self):
        self.privateKey = ""
        self.Node = Web3(Web3.HTTPProvider(server))
        self.contract = self.Node.eth.contract(address=Contract_addr, abi=Contract_abi)


    def Import_Keyfile(self, path, password):
        with open(path) as keyfile:
            encrypted_key = keyfile.read()
            self.privateKey = w3.eth.account.decrypt(encrypted_key, password)
        return self.privateKey

    ##### Fro Contract
    def new_AG_into_List(self, Kn, Address):
        ### 幫AG資訊至Smart Contract
        return

def Get_addressFormat(address):
    return Web3.toChecksumAddress(address)
