import os
import logging
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BATCH_SIZE = 100

def get_pinecone_index():
    api_key = os.getenv('PINECONE_API_KEY')
    index_name = "personalized-tests"  # Replace with your actual index name
    pc = Pinecone(api_key=api_key)
    return pc.Index(index_name)

async def delete_batch(index, ids):
    try:
        index.delete(ids=ids)
        logger.info(f"Successfully deleted batch of {len(ids)} vectors")
    except Exception as delete_error:
        logger.error(f"Error deleting batch: {str(delete_error)}")

async def delete_all_vectors_from_pinecone():
    try:
        index = get_pinecone_index()

        # Get all vector IDs
        stats = index.describe_index_stats()
        total_vector_count = stats['total_vector_count']
        logger.info(f"Total vectors in index: {total_vector_count}")

        # Fetch all vector IDs
        all_ids = []
        while len(all_ids) < total_vector_count:
            fetch_response = index.fetch(ids=list(range(len(all_ids), min(len(all_ids) + 10000, total_vector_count))))
            all_ids.extend(fetch_response['vectors'].keys())

        # Delete vectors in batches
        batches = [all_ids[i:i + BATCH_SIZE] for i in range(0, len(all_ids), BATCH_SIZE)]

        for batch in tqdm(batches, desc="Deleting vectors"):
            await delete_batch(index, batch)

        logger.info(f"Successfully deleted all {total_vector_count} vectors from Pinecone index.")

    except Exception as e:
        logger.error(f"Failed to delete vectors from Pinecone: {str(e)}")

if __name__ == "__main__":
    asyncio.run(delete_all_vectors_from_pinecone())
