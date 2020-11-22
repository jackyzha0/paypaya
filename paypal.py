# from dotenv import load_dotenv
# import os
import requests
from db import *

class PayPalClient:
    root_url = "https://api-m.sandbox.paypal.com"

    def __init__(self, phone):
        self.authstr = db.lookup_paypalauth(phone)
        self.token = "no token"
        self.setupToken()
        self.phone = phone

    def setupToken(self):
        url = self.root_url + "/v1/oauth2/token"
        payload = 'grant_type=client_credentials'
        headers = {
            'Authorization': f'Basic {self.authstr}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = requests.request("POST", url, headers=headers, data=payload)
        if r.status_code != 200:
            print("warn: did not get 200 from paypal auth")

        print(f"acquired scopes: {r.json()['scope']}")
        self.token = r.json()['access_token']

    def _constructPaypalAPICall(self, payload=None):
        url = self.root_url + "/v1/payments/payouts"
        api_headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        print(f"calling -> {url}")
        return requests.request("POST", url, headers=api_headers, json=payload)

    def _formulatePayload(self, id, subject, message, amt, recipient_email, note):
        return {
            "sender_batch_header": {
                "sender_batch_id": id,
                "email_subject": subject,
                "email_message": message,
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": amt,
                        "currency": "USD"
                    },
                    "note": note,
                    "sender_item_id": "201403140001",
                    "receiver": recipient_email,
                    "notification_language": "en-US"
                },
            ]
        }

    def pay(self, recipient_phone, amt):
        payload = self._formulatePayload(
            "payment_id",
            f"Payment from {self.phone}",
            f"Hey {recipient_phone}, {self.phone} sent you ${amt} with Paypaya!",
            amt,
            db.get_user(recipient_phone)['paypal_email'],
            f"{self.phone} sent you ${amt} with Paypaya!",
        )
        self._constructPaypalAPICall(payload=payload)


jacky = PayPalClient('+17789568798')
jacky.pay('+12368807768', 100)
