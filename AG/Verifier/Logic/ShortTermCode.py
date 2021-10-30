from ChameleonShort.Verifier import Verifier as sVer


class ShortTermCode:
    def __init__(self, Px, Py, q, kn, k):
        self.Px, self.Py, self.k, self.q = Px, Py, q, k
        self.sver = sVer(Px, Py, q, kn, k)
        self.kn = kn

    def makeSignature(self, msg):
        return self.sver.Signing(msg)

    def verifySignature(self, signature, msg, cliPubX, cliPubY):
        return self.sver.Verifying(msg, signature, cliPubX, cliPubY)
