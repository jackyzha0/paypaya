from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os
from db import *
import send
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

default_help_str = """Sorry, I couldn't understand what you were trying to do. To send money, reply with a message in this format 'SEND <phone-number> <amount>' \n If you want to add money to your account, send a message in this format 'ADD ###-###-#### $10
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
        resp.message(f"Thanks, {body}! You're good to go.")
        resp.message("To send money, reply with a message in this format 'SEND <phone-number> <amount>' \n If you want to add money to your account, send a message in this format 'ADD $10")
        return

    if user_info["onboarding_status"] == 1:

        if len(body.split(" ")) < 2:
            resp.message(default_help_str)
            return
        
        command = body.split(" ")[0]
        if (command == "SEND"):
            recipient = body.split(" ")[1]
            amt = int(body.split(" ")[2])

            print(
                f"received SEND targeted at {recipient} with amount {amt}"
            )

            sender = paypal.PayPalClient(sender_number)
            r = sender.pay(recipient, amt)
            if r.status_code > 300:
                resp.message(f"Uh oh! Something went wrong.")
                resp.message(r.json())
                return
            resp.message(f"Successfully sent ${amt} to {recipient}!")
            db.update_balance(sender_number, -1 * amt)
            db.update_balance(recipient, amt)
            resp.message(f"Your new balance is ${db.get_balance(sender_number)}")

            recipient_name = db.get_user(recipient)['name']
            send.SMS(
                recipient, f"Hey {recipient_name}, you just received a new payment of ${amt} from {sender_number}.")
            send.SMS(
                recipient, f"Your new balance is ${db.get_balance(recipient)}")
            return

        elif (command == "ADD"):
            amt = int(body.split(" ")[1])
            sender = paypal.Bank

            print(
                f"received ADD targeted at {sender_number} with amount {amt}"
            )

            r = sender.pay(sender_number, amt)
            if r.status_code > 300:
                resp.message(f"Uh oh! Something went wrong.")
                resp.message(r.json())
                return
            resp.message(f"Successfully deposited ${amt}!")
            db.update_balance(sender_number, amt)
            resp.message(f"Your new balance is ${db.get_balance(sender_number)}")
            return

        resp.message("To send money, reply with a message in this format 'SEND <phone-number> <amount>' \n If you want to add money to your account, send a message in this format 'ADD ###-###-#### $10")
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
