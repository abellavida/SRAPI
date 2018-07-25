from pymongo import MongoClient

##client = MongoClient()
client = MongoClient('ds249311.mlab.com', 49311)
db = client['carganwater']
db.authenticate('jcarter3','Carina1008!')
dbtemp = client.temp
