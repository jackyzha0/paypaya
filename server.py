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
    handle_sms(resp, sender, body)

    return str(resp)

default_help_str = """Sorry, I couldn't understand what you were trying to do. Here are some of the available commands:
    send $<amount> <phone-number>
    balance
    ...
"""

def handle_sms(resp, sender_number, body):
    
    # fetch user info from mongo using sender number
    user_info = db.get_user(sender_number)

    # not in database
    if not user_info:
        # onboarding flow step -1
        # create user in database
        print(f"new user, adding {sender_number} to database")
        
        # find first document in collection that has {is_used: false}
        email_obj = db.find_unused_email()
        print("found email obj")
        print(email_obj)

        # set that document is_used: true
        db.mark_email_as_used(email_obj['email'])
        print(f"marked {email_obj['email']} as used")

        new_user = User(email_obj['email'], sender_number)
        db.new_user(new_user)

        resp.message("Hi there! Thanks for signing up for Paypaya. Please respond with your name to complete the setup.")
        return

    print(f"fetched user info")
    print(user_info)

    # check onboarding status
    if user_info["onboarding_status"] == 0:
        # onboarding flow step 1
        # fill in name
        db.update_user({"phone": sender_number}, {"name": body, "onboarding_status": 1})
        resp.message(f"Thanks, {body}! You're good to go!")
        return
    
    if user_info["onboarding_status"] == 1:
        resp.message(f"Hi {name}! Would you like to send or add money?")
        resp.message("Message 1 to send money, message 2 to add money to your account")
        db.update_user({"transaction_command": 0}, {"transaction_command": body})

        if user_info["transaction_command"] == 1:
            resp.message("Enter the phone number of your recipient, followed by the $ amount you want to send")
            resp.message("Example: ###-###-#### $00")
            recipient = body.split(" $")[0]
            amt = body.split("$ ")[1]
            pay(sender, recipient, amt):
            return None

        db.update_user({}, {"transaction_command": 0})
        
    # unknown status/command, return default_help_str
    resp.message(default_help_str)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
