from pymongo import MongoClient

class JobDB:
    def __init__(self) -> None:
        self.client = MongoClient('mongodb://mongo-db:27017/')
        self.db = self.client['JobPostings']
        self.collection = self.db['karriereAT']
    def insert_jobs(self, jobs):
        job_data = [job.__dict__ for job in jobs]
        for job in job_data:
            self.collection.update_one({"job_hash":job["job_hash"]}, {"$set":job}, upsert=True)

    def get_items_to_update(self,skip=0, num_urls=100):
        cursor = self.collection.find({"is_active":True}, {}).sort("updated_at").skip(skip).limit(num_urls)
        urls = []
        for page in cursor:
            urls.append((page.get("_id"), page.get("url"), page.get("full_description")))
        return urls
    
    def update_item(self, updated_at, full_description, is_active, id):
        filter_condition = {'_id': id}
        update_data = {'$set': {'updated_at': updated_at, 'full_description': full_description, "is_active":is_active}}

        self.collection.update_one(filter_condition, update_data)

    def get_num_documents(self):
        return self.collection.count_documents({})
