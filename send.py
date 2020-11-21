from dotenv import load_dotenv
import os
from twilio.rest import Client


# load .env file
load_dotenv()

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
print(account_sid, auth_token)
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                    body="hi lovely",
                    from_='+18337290967',
                    to='+12368807768'
                )

print(message.sid)
