from dotenv import load_dotenv
import os
import requests

# load .env file
load_dotenv()
authstr = os.getenv('PAYPAL_AUTH_STR')

url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

payload = 'grant_type=client_credentials'
headers = {
    'Authorization': f'Basic {authstr}',
    'Content-Type': 'application/x-www-form-urlencoded'
}

token = ""
r = requests.request("POST", url, headers=headers, data=payload)
print(r.status_code)
if r.status_code != 200:
    print("warn: did not get 200 from paypal auth")

print(f"acquires scopes: {r.json()['scope']}")
token = r.json()['access_token']

def constructPaypalAPICall(type="GET", payload=None):
    url = "https://api-m.sandbox.paypal.com/v1/payments/payouts"
    api_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print(f"calling -> {url}")
    return requests.request(type, url, headers=api_headers, json=payload)


data = {
    "sender_batch_header": {
        "sender_batch_id": "Papaya Payout 0",
        "email_subject": "You have a payout!",
        "email_message": "You have received a payout! Thanks for using our service!"
    },
    "items": [
        {
            "recipient_type": "EMAIL",
            "amount": {
                "value": "420.69",
                "currency": "USD"
            },
            "note": "Thanks for your patronage!",
            "sender_item_id": "201403140001",
            "receiver": "0@paypaya.example.com",
            "notification_language": "en-US"
        },
    ]
}

r = constructPaypalAPICall(type="POST", payload = data)
print(r.status_code)
print(r.json())
