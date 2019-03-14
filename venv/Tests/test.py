from pymongo import MongoClient

client = MongoClient('mongodb+srv://Master:CiscoCLass@ssei-bwmef.mongodb.net/test?retryWrites=true')

db = client.test
colle = db['materialesTecnico']

pipeline = [{'$lookup':{
    'from': 'tecnico', 'localField': 'tecnico_ID', 'foreignField': '_id', 'as':'patatita'}
            },{'$lookup':{
    'from': 'material', 'localField': 'material_ID', 'foreignField': '_id', 'as':'pststito'}
            }
]
arrTemp = []
for doc in (colle.aggregate(pipeline)):
    arrTemp.append(doc)
print(arrTemp)