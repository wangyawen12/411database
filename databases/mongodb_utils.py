from pymongo import MongoClient, ASCENDING, errors
import pandas as pd
from pprint import pprint
from dotenv import load_dotenv
import os

load_dotenv()

CONNECTION_STRING = os.getenv('MONGODB_URL')
DATABASE = os.getenv('MONGODB_DATABASE')

def get_database():
 
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)
 
    # Create the database for our example (we will use the same database throughout the tutorial
    return client[DATABASE]
    
class MongoDB():
    def __init__(self):
        self.client = get_database()
        self.client["publications"].create_index([('id', ASCENDING)])
        self.client["publications"].create_index([('keywords.name', ASCENDING)])
        self.add_constraint()
    
    def add_constraint(self, maxYear=2024):
        validation_rule = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["year"],
                "properties": {
                    "year": {
                        "bsonType": "int",
                        "minimum": 1500,
                        "maximum": maxYear, 
                        "description": "must be an integer between 1500 and 2024 and is required"
                    }
                }
            }
        }
        # Publications = self.client["publications"]
        self.client.command({
            "collMod": "publications",
            "validator": validation_rule,
            "validationLevel": "strict"
        })
        print("Collection updated with validation.")
    
    def krc_by_entity(self, entity="Affiliation", keyword=None):
        Faculty = self.client["faculty"]
        entity_type = None
        if entity == "Affiliation":
            entity_type = "affiliation.name"
        elif entity == "Faculty":
            entity_type = "name"
        
        pipeline = [
            {"$project": {"_id": 0, entity_type: 1, "publications": 1}},
            {"$lookup": {
                "from": "publications",
                "localField": "publications",
                "foreignField": "id",
                "as": "publication_detail"
            }},
            {"$unwind": "$publication_detail"},
            {"$unwind": "$publication_detail.keywords"},
        ]
        if keyword is not None and keyword != '':
            pipeline.append({"$match": {"publication_detail.keywords.name": keyword}})
            
        pipeline.extend([
            {"$group": {
                "_id": "$" + entity_type,
                "total_KRC": {
                    "$sum": {
                        "$multiply": ["$publication_detail.keywords.score", "$publication_detail.numCitations"]
                    }
                }
            }},
            {"$sort": {"total_KRC": -1}},
            {"$limit": 25},
        ])

        result = Faculty.aggregate(pipeline)
        df = pd.DataFrame(list(result))
        
        df.rename(columns={'_id': entity}, inplace=True)
        
        return df
    
    # def get_publications(self):
    #     pipeline = [
    #         {'$project': {'_id': 0, 'id': 1, 'title': 1, 'year': 1, 'numCitations': 1, 'keywords': 1}},
    #         {'$limit': 5}
    #     ]
        
    #     Publications = self.client["publications"]
    #     result = Publications.aggregate(pipeline)
    #     df = pd.DataFrame(list(result))
    #     return df
    
    def update_publication(self, publication_id, content):
        # if field == 'keywords':
        #     field += '.$.score'
        Publications = self.client["publications"]

        try:
            result = Publications.update_one(
                {'id': publication_id},
                {'$set': content}
            )
            return self.get_publication_by_id(publication_id)
        except errors.WriteError as e:
            # print(f"WriteError: {e.details}")
            return False
        # pass

    def get_publication_id(self, faculty='Agouris,Peggy'):
        Faculty = self.client["faculty"]

        # result = Publications.aggregate([{"$project": {"_id": 0, "id": 1}}])
        result = Faculty.find({'name': f'{faculty}'}, {'_id': 0, 'publications': 1})
        temp = None
        for res in result:
            temp = res['publications']
        result = []
        for id in temp:
            result.append(str(id))
        return result
    
    def get_all_faculty(self):
        Faculty = self.client["faculty"]

        # result = Publications.aggregate([{"$project": {"_id": 0, "id": 1}}])
        result = Faculty.find({}, {'_id': 0, 'name': 1})
        temp = []
        for record in result:
            temp.append(record['name'])
        return temp
    
    def get_publication_by_id(self, publication_id):
        Publications = self.client["publications"]
        result = Publications.find(
            {'id': publication_id},
            {'_id': 0, 'title': 1, 'venue': 1, 'year': 1, 'numCitations': 1}
        )
        df = list(result)
        return df[0]
        

# mongodb = MongoDB()
# result = mongodb.get_all_faculty()
# print(result)
