from pymongo import MongoClient

client = MongoClient('mongodb+srv://paypaya-main:test@cluster0.5hure.mongodb.net/paypaya_db?retryWrites=true&w=majority')
db = client.get_database('paypaya_db')
records = db.user_records

//inserting new users
new_user = {
    "paypal_email": "addingtest@test.com",
    "name": "test adding name",
    "voice_identity":"test identity test"
}

records.insert_one(new_user)

//find documents
list(records.find())