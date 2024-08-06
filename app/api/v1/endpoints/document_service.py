from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from typing import List
from pydantic import BaseModel
import boto3
from langchain_openai import ChatOpenAI  # Updated import
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

def extract_test_info(ai_response_content):
    pattern = r'(\d+\.\s)(.*?)(?=:\s*Reason:|\.|\n|$)'
    test_infos = re.findall(pattern, ai_response_content)
    
    tests_with_reasons = []
    for idx, name in enumerate(test_infos):
        test_name = name[1].strip()
        reason_pattern = fr"{re.escape(name[0])}\s*{re.escape(test_name)}\s*:\s*Reason:(.*?)(?=\n\d|$)"
        reason_match = re.search(reason_pattern, ai_response_content, re.DOTALL)
        reason = reason_match.group(1).strip() if reason_match else "No reason provided."
        
        tests_with_reasons.append({
            "name": test_name,
            "reason": reason
        })
    
    return tests_with_reasons

@router.post("/recommend-tests")
async def recommend_tests(request: RecommendTestsRequest):
    try:
        # Initial prompt to get recommended tests
        prompt = f"Based on the health goals: {', '.join(request.healthGoals)} and the current diseases: {', '.join(request.currentDiseases)}, what are the best lab tests to recommend? Please provide a numbered list of specific test names with a brief reason for each test."

        ai_response = chat.invoke(
            [
                SystemMessage(content="You are an AI assistant trained to recommend lab tests. Provide specific test names along with reasons that would typically be found in a medical lab's catalog."),
                HumanMessage(content=prompt),
            ]
        )

        recommended_tests_info = extract_test_info(ai_response.content)
        index = get_pinecone_index()
        recommended_tests = []

        for test_info in recommended_tests_info:
            test_name = test_info["name"]

            # First, try an exact match
            exact_match = index.query(
                vector=[0] * VECTOR_DIMENSION,  # Dummy vector for metadata-only query
                filter={"Test Name": {"$eq": test_name}},
                top_k=1,
                include_metadata=True
            )

            if exact_match['matches']:
                test_metadata = exact_match['matches'][0]['metadata']
                reason = await get_test_reason_from_ai(test_name, request.healthGoals, request.currentDiseases)
                test_metadata['reason'] = reason
                recommended_tests.append(test_metadata)
                logger.info(f"Found exact match in Pinecone for: {test_name} with reason: {reason}")
            else:
                # If no exact match, use vector search as a fallback
                query_embedding = create_custom_embedding(test_name)
                query_response = index.query(
                    vector=query_embedding,
                    top_k=1,
                    include_metadata=True
                )

                if query_response['matches']:
                    test_metadata = query_response['matches'][0]['metadata']
                    reason = await get_test_reason_from_ai(test_name, request.healthGoals, request.currentDiseases)
                    test_metadata['reason'] = reason
                    recommended_tests.append(test_metadata)
                    logger.info(f"Found similar test in Pinecone for: {test_name} with reason: {reason}")
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

async def get_test_reason_from_ai(test_name: str, health_goals: List[str], current_diseases: List[str]) -> str:
    """
    Make an AI call to get the reason in a very layman way for recommending a specific lab test.
    """
    prompt = f"Why would a lab test named '{test_name}' be recommended for a patient with the health goals: {', '.join(health_goals)} and the current diseases: {', '.join(current_diseases)}?"
    
    ai_response = chat.invoke(
        [
            SystemMessage(content="You are an AI assistant trained to provide medical recommendations."),
            HumanMessage(content=prompt),
        ]
    )
    
    # Extract and return the reason from the AI response
    reason = ai_response.content.strip()
    return reason if reason else "No reason provided."

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
