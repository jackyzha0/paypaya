from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import os
from db import *
import twilio_client as twilio
import paypal

app = Flask(__name__)

azure_endpoint = "https://westus.api.cognitive.microsoft.com/sts/v1.0/issuetoken"

@app.route("/recording_cb/<phn>/<num>", methods=['POST'])
def statusCb(phn, num):
    sid = request.form.get('AccountSid')
    url = request.form.get('RecordingUrl')
    status = request.form.get('RecordingStatus')

    verification_url = f'{azure_endpoint}/speaker/verification/v2.0/text-dependent/profiles/{phn}/enrollments'

    print(f"got n={num} recording callback from {phn}. status={status}")
    if status == 'completed':
        # update onboarding status for user
        twilio.SMS(phn, "Thanks for verifying, Let's get started! \n\n To send money, reply with a message in this format 'SEND <recipient-phone-number> $00' \n \n To add money to your account, reply with a message in this format 'ADD $00' \n\n To withdraw funds to bank account, reply with a message in this format 'WITHDRAW $00' \n\n To view your balance, reply with 'BALANCE' \n\n")
        db.update_user({"phone": phn}, {
            "name": body, "onboarding_status": 2})
    else:
        print(f"shits busted")

@app.route('/recording_finished', methods=['GET', 'POST'])
def finished():
    return  """<?xml version="1.0" encoding="UTF-8"?>
                <Response>
                <Say>Thank you for setting up voice authentication. Check your text messages for next steps.</Say>
                </Response>
            """

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


default_help_str = """Sorry, I couldn't understand what you were trying to do.
"""

info_str = "To send money, reply with a message in this format 'SEND <recipient-phone-number> $00' \n \n To add money to your account, reply with a message in this format 'ADD $00' \n\n To withdraw funds to bank account, reply with a message in this format 'WITHDRAW $00' \n\n To view your balance, reply with 'BALANCE' \n\n"


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

        resp.message(
            "Hi there! Thanks for signing up for Paypaya. Please respond with your name to complete the setup.")
        return

    print(f"fetched user info")
    print(user_info)

    # check onboarding status
    if user_info["onboarding_status"] == 0:
        # onboarding flow step 1
        # fill in name
        db.update_user({"phone": sender_number}, {
                       "name": body, "onboarding_status": 1})
        resp.message(f"Thanks, {body}! Now let's add some security measures by adding your voice as a passcode. You will need to verify any payments over $30 via a phone call.")
        resp.message(
            f"Now, we'll quickly call you and ask you to repeat a few phrases back to us.")
        twilio_client.Call(sender_number)
        return

    if user_info["onboarding_status"] == 1:
        # user never finished onboarding, redirect them back to this flow
        resp.message(
            f"Looks like you never finished verifying your voice! Let's fix that.")
        twilio_client.Call(sender_number)
        return

    if user_info["onboarding_status"] == 2:
        parts = body.split(" ")

        command = parts[0]

        if (command == "BALANCE"):
            resp.message(f"Your account balance is ${db.get_balance(sender_number)}")
            return

        if len(parts) < 1:
            resp.message(default_help_str)
            resp.message(info_str)
            return

        if (command == "ADD"):
            amt = int(parts[1])
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
            resp.message(
                f"Your new balance is ${db.get_balance(sender_number)}")
            return

        if (command == "WITHDRAW"):
            amt = int(parts[1])
            sender = paypal.PayPalClient(sender_number)
            r = sender.pay(paypal.Bank, amt)
            if r.status_code > 300:
                resp.message(f"Uh oh! Something went wrong.")
                resp.message(r.json())
                return 
            resp.message(f"Successfully withdrew ${amt}!")
            db.update_balance(sender_number, -1 * amt)
            return

        if len(parts) < 2:
            resp.message(default_help_str)
            resp.message(info_str)
            return

        if (command == "SEND"):
            recipient = parts[1]
            amt = int(parts[2])

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
            resp.message(
                f"Your new balance is ${db.get_balance(sender_number)}")

            recipient_name = db.get_user(recipient)['name']
            twilio.SMS(
                recipient, f"Hey {recipient_name}, you just received a new payment of ${amt} from {sender_number}.")
            twilio.SMS(
                recipient, f"Your new balance is ${db.get_balance(recipient)}")
            return

        resp.message(info_str)
        
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
