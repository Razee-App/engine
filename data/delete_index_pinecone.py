import os
import logging
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
from tqdm.asyncio import tqdm_asyncio

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BATCH_SIZE = 100
MAX_ATTEMPTS = 5

def get_pinecone_index():
    api_key = os.getenv('PINECONE_API_KEY')
    environment = os.getenv('PINECONE_ENVIRONMENT')
    index_name = os.getenv('PINECONE_INDEX_NAME', 'personalized-tests')
    pc = Pinecone(api_key=api_key, environment=environment)
    return pc.Index(index_name)

async def delete_batch(index, ids):
    try:
        index.delete(ids=ids)
        logger.info(f"Successfully deleted batch of {len(ids)} vectors")
        return len(ids)
    except Exception as delete_error:
        logger.error(f"Error deleting batch: {str(delete_error)}")
        return 0

async def fetch_all_ids(index, total_vector_count):
    all_ids = []
    fetch_limit = 10000  # Increased back to 10000

    try:
        logger.debug(f"Attempting to fetch up to {total_vector_count} IDs")
        response = index.query(
            vector=[0] * index.describe_index_stats()['dimension'],
            top_k=total_vector_count,
            include_metadata=True,
            include_values=False
        )
        all_ids = [match['id'] for match in response['matches']]
        logger.info(f"Fetched {len(all_ids)} IDs using query method")
    except Exception as fetch_error:
        logger.error(f"Error fetching IDs: {str(fetch_error)}")
    
    return all_ids

async def delete_all_vectors_from_pinecone():
    try:
        index = get_pinecone_index()
        attempt = 0

        while attempt < MAX_ATTEMPTS:
            # Get current vector count
            stats = index.describe_index_stats()
            total_vector_count = stats['total_vector_count']
            logger.info(f"Current total vectors in index: {total_vector_count}")
            
            if total_vector_count == 0:
                logger.info("All vectors have been deleted. Exiting.")
                return

            # Fetch all vector IDs
            all_ids = await fetch_all_ids(index, total_vector_count)
            logger.info(f"Fetched a total of {len(all_ids)} vector IDs")

            if not all_ids:
                logger.warning("No vector IDs fetched. Trying again...")
                attempt += 1
                continue

            # Delete vectors in batches
            batches = [all_ids[i:i + BATCH_SIZE] for i in range(0, len(all_ids), BATCH_SIZE)]
            delete_tasks = [delete_batch(index, batch) for batch in batches]
            deleted_counts = await tqdm_asyncio.gather(*delete_tasks, desc="Deleting vectors")
            
            total_deleted = sum(deleted_counts)
            logger.info(f"Total vectors deleted in this iteration: {total_deleted}")

            # Check if we made progress
            if total_deleted == 0:
                logger.warning("No vectors were deleted in this iteration. Trying again...")
                attempt += 1
            else:
                attempt = 0  # Reset attempt counter if we made progress

        logger.warning(f"Reached maximum attempts ({MAX_ATTEMPTS}). Some vectors may remain.")

    except Exception as e:
        logger.error(f"Failed to delete vectors from Pinecone: {str(e)}")

    finally:
        # Final count check
        try:
            final_stats = index.describe_index_stats()
            final_count = final_stats['total_vector_count']
            logger.info(f"Final vector count in index: {final_count}")

            if final_count == 0:
                logger.info("All vectors successfully deleted.")
            else:
                logger.warning(f"Not all vectors were deleted. {final_count} vectors remain.")
        except Exception as e:
            logger.error(f"Error checking final vector count: {str(e)}")

if __name__ == "__main__":
    asyncio.run(delete_all_vectors_from_pinecone())