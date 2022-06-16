# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client


if __name__ == '__main__':

    # Find your Account SID and Auth Token at twilio.com/console
    # and set the environment variables. See http://twil.io/secure
    account_sid = "ACb87d7dccffb45d6824d4925770536d7d"
    auth_token = "e694f91896a6bb6472589880f6477bb8"
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body="Join Earth's mightiest heroes. Like Kevin Bacon.",
        from_='+61 480 017 104',
        to='+886966095723'
    )