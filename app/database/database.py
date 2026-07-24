import os
from pymongo import MongoClient
from datetime import datetime

class Database:
    def __init__(self):
        uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("DATABASE_NAME", "anihub")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.series_col = self.db["series"]
        self.episodes_col = self.db["episodes"]
        
        # Indexes for fast upsert
        self.series_col.create_index("series_id", unique=True)
        self.episodes_col.create_index([("series_id", 1), ("season", 1), ("episode", 1)], unique=True)
    
    def upsert_series(self, data):
        """Insert or update series"""
        data["last_updated"] = datetime.utcnow()
        self.series_col.update_one(
            {"series_id": data["series_id"]},
            {"$set": data},
            upsert=True
        )
    
    def upsert_episode(self, data):
        """Insert or update episode"""
        data["last_checked"] = datetime.utcnow()
        filter = {
            "series_id": data["series_id"],
            "season": data["season"],
            "episode": data["episode"]
        }
        self.episodes_col.update_one(filter, {"$set": data}, upsert=True)
    
    def get_all_series(self):
        return list(self.series_col.find({}, {"_id": 0}))
    
    def get_series_by_id(self, series_id):
        return self.series_col.find_one({"series_id": series_id}, {"_id": 0})
    
    def get_episodes(self, series_id, season=None):
        query = {"series_id": series_id}
        if season:
            query["season"] = season
        return list(self.episodes_col.find(query, {"_id": 0}).sort("episode", 1))
    
    def get_stats(self):
        return {
            "series": self.series_col.count_documents({}),
            "episodes": self.episodes_col.count_documents({})
        }
