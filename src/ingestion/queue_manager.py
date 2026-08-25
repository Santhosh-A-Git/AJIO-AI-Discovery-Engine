import os
import json
# pyrefly: ignore [missing-import]
import redis
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

class QueueManager:
    def __init__(self):
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.queue_name = 'raw_ingestion_queue'
        self.redis_client = None
        self.use_mock = False
        
        try:
            self.redis_client = redis.Redis(host=self.host, port=self.port, db=0)
            # Test connection
            self.redis_client.ping()
            print(f"Connected to Redis at {self.host}:{self.port}")
        except redis.ConnectionError:
            print(f"Warning: Could not connect to Redis at {self.host}:{self.port}.")
            print("Falling back to Mock Queue (data will just be printed/logged).")
            self.use_mock = True

    def publish_batch(self, items):
        """
        Publishes a batch of scraped items to the queue.
        """
        if not items:
            return

        if self.use_mock:
            print(f"[Mock Queue] Published {len(items)} items to queue.")
            return

        pipeline = self.redis_client.pipeline()
        for item in items:
            pipeline.rpush(self.queue_name, json.dumps(item))
        pipeline.execute()
        
        print(f"Successfully published {len(items)} items to Redis queue '{self.queue_name}'.")

    def consume_batch(self, batch_size=100):
        """
        Consumes a batch of items from the queue.
        """
        if self.use_mock:
            print(f"[Mock Queue] Attempted to consume {batch_size} items. Returning empty list.")
            return []

        items = []
        for _ in range(batch_size):
            item = self.redis_client.lpop(self.queue_name)
            if item:
                items.append(json.loads(item))
            else:
                break
                
        return items

if __name__ == "__main__":
    # Test run
    qm = QueueManager()
    qm.publish_batch([{"test": "data"}])
