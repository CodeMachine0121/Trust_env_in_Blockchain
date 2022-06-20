import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
serviceID = os.environ["TWILIO_SERVICE_ID"]


def sendOneTimePassword_SMS(phoneNumber: str):
    # 電話號碼要去掉頭一個字 0
    client = Client(account_sid, auth_token)
    verification = client.verify \
        .services(serviceID) \
        .verifications \
        .create(to='+886{}'.format(phoneNumber[1:]), channel='sms')

def verifyOneTimePassword_SMS(phoneNumber: str, otp: str) -> bool:
    client = Client(account_sid, auth_token)
    try:
        verification = client.verify \
            .services(serviceID) \
            .verification_checks \
            .create(to='+886{}'.format(phoneNumber[1:]), code=otp).status
    except TwilioRestException as e:
        print("[!] TwilioRestException occur")
        verification = True
    return True if verification == "approved" else False


