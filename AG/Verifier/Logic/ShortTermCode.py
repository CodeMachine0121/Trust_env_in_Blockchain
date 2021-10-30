from ChameleonShort.Verifier import Verifier as sVer


class ShortTermCode:
    def __init__(self, Px, Py, q, kn, k):
        self.Px, self.Py, self.k, self.q = Px, Py, q, k
        self.sver = sVer(Px, Py, q, kn, k)
        self.kn = kn
        self.sessionKey_List = {}

    def makeSignature(self, msg):
        return self.sver.Signing(msg)

    def verifySignature(self, signature, msg, cliPubX, cliPubY):
        return self.sver.Verifying(msg, signature, cliPubX, cliPubY)

    def SessionKey(self):
        return self.sver.Session_key_Exchange()

    def setSessionKey(self, Kx, Ky):
        sk, CHash = self.sver.set_Session_key(Kx, Ky)
        self.sessionKey_List[Kx] = {'sk':sk, 'CHash':CHash}
        return
