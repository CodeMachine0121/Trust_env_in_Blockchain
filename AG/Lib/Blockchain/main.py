from web3 import HTTPProvider, Web3
from web3.auto import w3


class Ethereum:
    def __init__(self):
        self.server = '192.168.1.184:8545'
        self.privateKey = ""
        self.Node = None

    def make_Connection_to_Node(self):
        self.Node = HTTPProvider("http://{}".format(self.server))
        return self.Node

    def Import_Keyfile(self, path, password):
        with open(path) as keyfile:
            encrypted_key = keyfile.read()
            self.privateKey = w3.eth.account.decrypt(encrypted_key, password)
        return self.privateKey

    def make_rawTransaction(self, txnInfo):
        """
        :param txnInfo:
        {
             'from':
             'to': '0xF0109fC8DF283027b6285cc889F5aA624EaC1F55',
             'data': "Hello world"
             'value': 1000000000,
             'gas': 2000000,
             'gasPrice': 234567897654321,
             'nonce': 0,
             'chainId': 1
        }
        """
        ## 發送方需要跟keyfile裡的私鑰一致
        signed_txn = w3.eth.account.sign_transaction(txnInfo, self.privateKey)

        rawTxn = signed_txn.rawTransaction

        tmp = w3.eth.sendRawTransaction(rawTxn.hex())

        return rawTxn.hex()


def Get_addressFormat(address):
    return w3.toChecksumAddress(address)
