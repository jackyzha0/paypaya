from pymongo import MongoClient
class Db:
    def __init__(self, connection_url, database_name):
        self.client = MongoClient(connection_url)
        self.db = self.client.get_database(database_name)
        self.records = self.db.user_records
        self.emails = self.db.paypal_accounts
    
    def new_user(self, user):
        self.records.insert_one(user.__dict__)
        print(f"successfully inserted new user {user.phone}")
    
    def get_user(self, phone):
        return self.records.find_one({"phone": phone})

    def update_balance(self, phone, amt):
        self.records.update_one({"phone": phone}, {'$inc': {"balance": amt}})

    def get_balance(self, phone):
        return int(self.get_user(phone)['balance'])

    def update_user(self, filter, update_value):
        self.records.update_one(filter, {'$set': update_value})

    #find unused email
    def find_unused_email(self):
        return self.emails.find_one({"is_used": False})

    def mark_email_as_used(self, email):
        self.emails.update_one({"email": email}, {'$set': {"is_used" : True}})

    def lookup_paypalauth(self, phone):
        email = self.get_user(phone)['paypal_email']
        return self.emails.find_one({"email": email})['paypal_auth']
        

class User:
    def __init__(self, email, phone, balance=5000):
        self.name = "placeholder_name"
        self.phone = phone
        self.paypal_email = email
        self.voice_identity = ""
        self.onboarding_status = 0
        self.balance = balance

db = Db('mongodb+srv://paypaya-main:test@cluster0.5hure.mongodb.net/paypaya_db?retryWrites=true&w=majority', 'paypaya_db')


# new_user = User("name test", "phone test")
# db.new_user(new_user)
# print(db.get_user("phone test"))
# db.update_user({"name": "name test"}, {"name": 'yeet'})
