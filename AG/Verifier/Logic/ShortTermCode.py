from .ChameleonShort.Verifier import Verifier as sVer


class ShortTermCode:
    def __init__(self, Px, Py, q, kn, k):
        self.Px, self.Py, self.k, self.q = Px, Py, q, k
        self.sver = sVer(Px, Py, q, kn, k)
        #self.kn = kn
        self.sessionKey_List = {}

    def SessionKey(self):
        return self.sver.Session_key_Exchange()  # xp.x, xp.y

    def setSessionKey(self, Kx, Ky, Knx):
        sk, CHash = self.sver.set_Session_key(Kx, Ky)
        self.sessionKey_List[Knx] = {'sk': sk, 'CHash': CHash}
        return

    def makeSignature(self, msg, cliPubX):
        sk = self.sessionKey_List[cliPubX]["sk"]
        return self.sver.Signing(msg, sk)

    def verifySignature(self, signature, msg, cliPubX, cliPubY):
        chash = self.sessionKey_List[cliPubX]["CHash"]
        return self.sver.Verifying(
            msg, signature, cliPubX, cliPubY, chash)
