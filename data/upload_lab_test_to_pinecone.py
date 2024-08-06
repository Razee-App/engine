import pandas as pd
import numpy as np
from pinecone import Pinecone
from dotenv import load_dotenv
import os
import json
import logging
import asyncio
from tqdm import tqdm
import tiktoken

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VECTOR_DIMENSION = 1536
BATCH_SIZE = 100
MAX_TOKENS = 8191

def get_pinecone_index():
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    return pc.Index("personalized-tests")  # Replace with your actual index name

def clean_data(data):
    cleaned = {}
    for k, v in data.items():
        if pd.isna(v):
            if k == 'Price (AED)':
                cleaned[k] = 0  # Use 0 for null numeric values
            else:
                cleaned[k] = ""  # Use empty string for null string values
        else:
            cleaned[k] = v
    return cleaned

def create_custom_embedding(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)[:MAX_TOKENS]
    
    embedding = np.zeros(VECTOR_DIMENSION)
    for token in tokens:
        embedding[token % VECTOR_DIMENSION] += 1
    
    norm = np.linalg.norm(embedding)
    if norm != 0:
        embedding = embedding / norm
    
    return embedding.tolist()

async def upload_batch(index, batch):
    try:
        await asyncio.to_thread(index.upsert, vectors=batch)
        logger.info(f"Successfully upserted batch of {len(batch)} items")
    except Exception as upsert_error:
        logger.error(f"Error upserting batch: {str(upsert_error)}")
        logger.error(f"Problematic batch: {json.dumps(batch)}")

async def upload_lab_tests_to_pinecone():
    try:
        lab_tests_df = pd.read_csv("data/datasets/lab_tests_ingested_with_descriptions_final.csv")
        index = get_pinecone_index()

        batches = []
        current_batch = []

        for _, row in tqdm(lab_tests_df.iterrows(), total=len(lab_tests_df)):
            test_id = row['Test ID']
            test_info = clean_data({
                "Test ID": row['Test ID'],
                "CPT Code": row['CPT Code'],
                "Test Name": row['Test Name'],
                "Sample Type": row['Sample Type'],
                "Container": row['Container'],
                "TAT": row['TAT'],
                "Price (AED)": row['Price (AED)'],
                "Description": row['Description']
            })
            
            text_to_embed = f"{test_info['Test Name']} {test_info['Description']}"
            embedding = create_custom_embedding(text_to_embed)

            current_batch.append({
                'id': str(test_id),
                'values': embedding,
                'metadata': test_info
            })

            if len(current_batch) == BATCH_SIZE:
                batches.append(current_batch)
                current_batch = []

        if current_batch:
            batches.append(current_batch)

        await asyncio.gather(*[upload_batch(index, batch) for batch in batches])

        logger.info("Lab tests data upload to Pinecone completed!")
    
    except Exception as e:
        logger.error(f"Failed to upload lab tests data to Pinecone: {str(e)}")

if __name__ == "__main__":
    asyncio.run(upload_lab_tests_to_pinecone())