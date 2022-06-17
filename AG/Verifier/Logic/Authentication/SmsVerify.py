import os
from twilio.rest import Client


class SMSAuthentication:
    def __init__(self):
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        self.serviceID = os.environ["TWILIO_SERVICE_ID"]
        self.client = Client(account_sid, auth_token)

    def sendOneTimePassword_SMS(self, phoneNumber: str):
        # 電話號碼要去掉頭一個字 0
        verification = self.client.verify \
            .services(self.serviceID) \
            .verifications \
            .create(to='+886{}'.format(phoneNumber[1:]), channel='sms')

    def verifyOneTimePassword_SMS(self, phoneNumber: str, otp: str) -> bool:
        verification = self.client.verify \
            .services(self.serviceID) \
            .verification_checks \
            .create(to='+886{}'.format(phoneNumber[1:]), code=otp).status
        return True if verification == "approved" else False


