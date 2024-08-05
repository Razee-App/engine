from fastapi import APIRouter, Form, HTTPException
from typing import List
import pandas as pd
import numpy as np
from pinecone import Pinecone
from sklearn.feature_extraction.text import TfidfVectorizer
from app.core.config import Config
import os

router = APIRouter()
config = Config()

VECTOR_DIMENSION = 1536  # Set this to match your Pinecone index dimension

def get_pinecone_index():
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    return pc.Index("personalized-tests")  # Replace with your actual index name

def simple_embed(text):
    vectorizer = TfidfVectorizer()
    vector = vectorizer.fit_transform([text]).toarray()[0]
    
    if len(vector) < VECTOR_DIMENSION:
        padding = np.zeros(VECTOR_DIMENSION - len(vector))
        vector = np.concatenate([vector, padding])
    else:
        vector = vector[:VECTOR_DIMENSION]
    
    return vector.tolist()

@router.post("/recommend-tests")
async def recommend_tests(
    healthGoals: List[str] = Form(...),
    currentDiseases: List[str] = Form(...),
    userId: str = Form(...)
):
    try:
        # Load the lab tests data
        lab_tests_df = pd.read_csv("app/datasets/Lab-Tests-Sample.csv")
        
        # Prepare the prompt
        prompt = f"Health Goals: {', '.join(healthGoals)}. Current Diseases: {', '.join(currentDiseases)}"

        # Generate embeddings using our simple embed function
        user_embedding = simple_embed(prompt)

        # Query Pinecone to find similar lab tests based on embeddings
        index = get_pinecone_index()
        query_result = index.query(vector=user_embedding, top_k=5, include_values=True)

        # Extract test names and details for the recommended lab tests
        recommended_tests = []
        for match in query_result['matches']:
            test_id = match['id']
            test_info = lab_tests_df[lab_tests_df['Test ID'] == int(test_id)].to_dict('records')
            if test_info:  # Check if a matching test was found
                recommended_tests.extend(test_info)
            else:
                print(f"Warning: No test found for ID {test_id}")

        return {
            "userId": userId,
            "recommendedTests": recommended_tests
        }

    except Exception as e:
        print(f"Error in recommend_tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))