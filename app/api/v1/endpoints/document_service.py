from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from typing import List
from pydantic import BaseModel
import boto3
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.core.config import Config
from dotenv import load_dotenv
import logging
import re
from pinecone import Pinecone
import os
import numpy as np
import tiktoken

# Load environment variables from .env file
load_dotenv()

router = APIRouter()
config = Config()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'.jpeg', '.jpg', '.png', '.pdf', '.txt'}
VECTOR_DIMENSION = 1536  # Set this to match your Pinecone index dimension
MAX_TOKENS = 8191  # Define the maximum number of tokens you want to use

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ChatOpenAI with AI71 Falcon-180B model
chat = ChatOpenAI(
    model="tiiuae/falcon-180B-chat",
    api_key=config.AI71_API_KEY,
    base_url="https://api.ai71.ai/v1/",
    streaming=False,
)

class RecommendTestsRequest(BaseModel):
    healthGoals: List[str]
    currentDiseases: List[str]
    userId: str

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.S3_REGION
    )

def get_pinecone_index():
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    return pc.Index("personalized-tests")  # Replace with your actual index name

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

def extract_test_names(ai_response_content):
    test_name_pattern = r'(?<=\d\.\s)(.*?)(?=:|\.|\n|$)'
    test_names = re.findall(test_name_pattern, ai_response_content)
    return [name.strip() for name in test_names if name.strip()]

@router.post("/recommend-tests")
async def recommend_tests(request: RecommendTestsRequest):
    try:
        prompt = f"Based on the health goals: {', '.join(request.healthGoals)} and the current diseases: {', '.join(request.currentDiseases)}, what are the best lab tests to recommend? Please provide a numbered list of specific test names."

        ai_response = chat.invoke(
            [
                SystemMessage(content="You are an AI assistant trained to recommend lab tests. Provide specific test names that would typically be found in a medical lab's catalog."),
                HumanMessage(content=prompt),
            ]
        )

        recommended_test_names = extract_test_names(ai_response.content)
        index = get_pinecone_index()
        recommended_tests = []

        for test_name in recommended_test_names:
            # First, try an exact match
            exact_match = index.query(
                vector=[0] * VECTOR_DIMENSION,  # Dummy vector for metadata-only query
                filter={"Test Name": {"$eq": test_name}},
                top_k=1,
                include_metadata=True
            )

            if exact_match['matches']:
                test_info = exact_match['matches'][0]['metadata']
                recommended_tests.append(test_info)
                logger.info(f"Found exact match in Pinecone for: {test_name}")
            else:
                # If no exact match, use vector search as a fallback
                query_embedding = create_custom_embedding(test_name)
                query_response = index.query(
                    vector=query_embedding,
                    top_k=1,
                    include_metadata=True
                )

                if query_response['matches']:
                    test_info = query_response['matches'][0]['metadata']
                    recommended_tests.append(test_info)
                    logger.info(f"Found similar test in Pinecone for: {test_name}")
                else:
                    logger.warning(f"No matching lab test found in Pinecone for: {test_name}")

        if not recommended_tests:
            logger.info("No relevant lab tests found based on the AI recommendation")
            raise HTTPException(status_code=404, detail="No relevant lab tests found")

        return {
            "userId": request.userId,
            "recommendedTests": recommended_tests
        }

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/upload-lab-tests")
async def upload_lab_tests(
    hasLabTest: bool = Form(...),
    hasMedicalReport: bool = Form(...),
    userId: str = Form(...),
    labTestFiles: List[UploadFile] = File(None),
    medicalReportFiles: List[UploadFile] = File(None)
):
    try:
        s3_client = get_s3_client()
        bucket_name = config.S3_BUCKET

        lab_test_urls = []
        medical_report_urls = []

        if labTestFiles:
            for file in labTestFiles:
                validate_file(file)
                s3_key = f'lab_tests/{userId}/{file.filename}'
                s3_client.upload_fileobj(file.file, bucket_name, s3_key)
                lab_test_urls.append(f"https://{bucket_name}.s3.amazonaws.com/{s3_key}")

        if medicalReportFiles:
            for file in medicalReportFiles:
                validate_file(file)
                s3_key = f'medical_reports/{userId}/{file.filename}'
                s3_client.upload_fileobj(file.file, bucket_name, s3_key)
                medical_report_urls.append(f"https://{bucket_name}.s3.amazonaws.com/{s3_key}")

        return {
            "message": "Lab test information received and files uploaded successfully",
            "labTestUrls": lab_test_urls,
            "medicalReportUrls": medical_report_urls
        }

    except HTTPException as http_exp:
        raise http_exp
    except Exception as e:
        logger.error(f"Error uploading files: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while uploading files")

@router.get("/print-config")
async def print_config():
    try:
        config_values = {
            'SECRET_KEY': config.SECRET_KEY,
            'AWS_ACCESS_KEY_ID': config.AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': config.AWS_SECRET_ACCESS_KEY,
            'S3_REGION': config.S3_REGION,
            'S3_BUCKET': config.S3_BUCKET,
            'KMS_KEY_ID': config.KMS_KEY_ID,
            'AI71_API_KEY': config.AI71_API_KEY,
            'PINECONE_API_KEY': config.PINECONE_API_KEY,
            'PINECONE_REGION': config.PINECONE_REGION
        }
        return config_values
    
    except Exception as e:
        logger.error(f"Error retrieving config values: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving config values")

def validate_file(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the limit")
    
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")
