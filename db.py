from pymongo import MongoClient
class Db:
    def __init__(self, connection_url, database_name):
        self.client = MongoClient(connection_url)
        self.db = self.client.get_database(database_name)
        self.records = self.db.user_records
    
    def new_user(self, user):
        self.records.insert_one(user.__dict__)
        print(f"successfully inserted new user {user.phone}")
    
    def get_user(self, phone):
        return self.records.find_one({"phone": phone})

    def update_user(self, filter, update_value):
        self.records.update_one(filter, {'$set': update_value})

class User:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone
        self.paypal_email = ""
        self.voice_identity = ""
        self.onboarding_status = 0

db = Db( 'mongodb+srv://paypaya-main:test@cluster0.5hure.mongodb.net/paypaya_db?retryWrites=true&w=majority', 'paypaya_db')


# new_user = User("name test", "phone test")
# db.new_user(new_user)
# print(db.get_user("phone test"))
# db.update_user({"name": "name test"}, {"name": 'yeet'})
