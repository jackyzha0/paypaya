from dotenv import load_dotenv
import os
from twilio.rest import Client


# load .env file
load_dotenv()

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

def SMS(to, message):
    message = client.messages \
        .create(
            body=message,
            from_='+18337290967',
            to=to,
        )