import pyotp


if __name__ == '__main__':
    out = pyotp.totp.TOTP('JBSWY3DPEHPK3PXP').provisioning_uri(
        name='asdfg55887@google.com', issuer_name='Secure App')
    print(out)
    otp = pyotp.TOTP('JBSWY3DPEHPK3PXP')
    print(otp.now())