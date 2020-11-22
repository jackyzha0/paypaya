from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os
from db import *
import paypal

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
        resp.message(f"Thanks, {body}! You're good to go! Text 'help' for more info")
        return

    if user_info["onboarding_status"] == 1:

        if len(body.split(" ")) < 2:
            resp.message(default_help_str)
            return

        resp.message("To send money, reply with a message in this format 'SEND ###-###-#### $10' \n If you want to add money to your account, send a message in this format 'ADD ###-###-#### $10")
        
        command = body.split(" ")[0]
        recipient = body.split(" ")[1]
        amt = int(body.split(" ")[2])

        print(f"received command {command} targeted at {recipient} with amount {amt}")

        if (command == "SEND"):
            sender = paypal.PayPalClient(sender_number)
            sender.pay(recipient, amt)
        elif (command == "ADD"):
            send(recipient, amt)   

        db.update_user({}, {"transaction_command": 0})
    

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
