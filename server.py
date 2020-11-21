from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os
from db import *

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)
    sender = request.values.get('From')

    print(f"message received from {sender}! received body: {body}")

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    resp.message(handle_sms(sender, body))

    return str(resp)

default_help_str = """Sorry, I couldn't understand what you were trying to do. Here are some of the available commands:
    send $<amount> <phone-number>
    balance
    ...
"""

def handle_sms(sender_number, body):
    # fetch user info from mongo using sender number
    user_info = db.get_user(sender)

    # not in database
    if not user_info:
        # onboarding flow step -1
        # create user in database
        print(f"new user, adding {sender_number} to database")
        new_user = User("placeholder_name", sender_number)
        db.new_user(new_user)

        return "Hi there! Thanks for signing up for Paypaya. Please respond with your name to complete the setup."

    # check onboarding status
    if user_info.onboarding_status == 0:
        # onboarding flow step 1
        # fill in name
        db.update_user({"phone": sender_number}, {"name": body})
        return f"Thanks, ${body}! You're good to go!"

    # unknown status/command, return default_help_str
    return default_help_str

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
