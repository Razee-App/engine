from fastapi import APIRouter, UploadFile, File, HTTPException
import boto3
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI
from app.core.config import Config

router = APIRouter()
config = Config()

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.S3_REGION
    )

def get_langchain():
    llm = OpenAI(model="text-davinci-003")  # Update model if needed
    return LLMChain(llm=llm)

@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    try:
        # Validate file type and size
        if not file.content_type.startswith('text'):
            raise HTTPException(status_code=400, detail="Invalid file type or empty file")

        s3_client = get_s3_client()
        bucket_name = config.S3_BUCKET
        s3_key = f'documents/{file.filename}'  # Customize path as needed

        # Upload file to S3
        s3_client.upload_fileobj(file.file, bucket_name, s3_key)

        # Process document with LangChain
        file.file.seek(0)  # Move cursor to the start of the file
        langchain = get_langchain()
        text = langchain.run(file.file.read().decode('utf-8'))  # Ensure the file is read as a string

        # Optionally add text to document repository
        # Your code to add text to a repository

        return {"text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    try:
        bucket_name = config.S3_BUCKET
        s3_key = f'test/{file.filename}'  # Use a specific path or filename for testing

        s3_client = get_s3_client()
        s3_client.upload_fileobj(file.file, bucket_name, s3_key)

        return {"message": f'File uploaded to {bucket_name}/{s3_key}'}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/print-config")
async def print_config():
    try:
        config_values = {
            'SECRET_KEY': config.SECRET_KEY,
            'AWS_ACCESS_KEY_ID': config.AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': config.AWS_SECRET_ACCESS_KEY,
            'S3_REGION': config.S3_REGION,
            'S3_BUCKET': config.S3_BUCKET,
            'KMS_KEY_ID': config.KMS_KEY_ID
        }
        return config_values
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
