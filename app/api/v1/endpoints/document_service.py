from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
import boto3
from langchain.chains import LLMChain
from langchain_community.llms import OpenAI
from app.core.config import Config
import os

router = APIRouter()
config = Config()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {'.jpeg', '.jpg', '.png', '.pdf', '.txt'}  # Added .txt for document uploads

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

def validate_file(file: UploadFile):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the limit")
    
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type")

@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    try:
        validate_file(file)
        if not file.content_type.startswith('text'):
            raise HTTPException(status_code=400, detail="Invalid file type for document upload")

        s3_client = get_s3_client()
        bucket_name = config.S3_BUCKET
        s3_key = f'documents/{file.filename}'

        s3_client.upload_fileobj(file.file, bucket_name, s3_key)

        #file.file.seek(0)
        #langchain = get_langchain()
        #text = langchain.run(file.file.read().decode('utf-8'))

        return {
            "message": "Document uploaded and processed successfully",
            "text": text,
            "s3_url": f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        }
    
    except HTTPException as http_exp:
        raise http_exp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lab-test")
async def upload_lab_test(
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

        # Here you would typically save the data to your database
        # For example:
        # save_lab_test_data(userId, hasLabTest, hasMedicalReport, lab_test_urls, medical_report_urls)

        return {
            "message": "Lab test information received and files uploaded successfully",
            "labTestUrls": lab_test_urls,
            "medicalReportUrls": medical_report_urls
        }

    except HTTPException as http_exp:
        raise http_exp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    try:
        validate_file(file)
        bucket_name = config.S3_BUCKET
        s3_key = f'test/{file.filename}'

        s3_client = get_s3_client()
        s3_client.upload_fileobj(file.file, bucket_name, s3_key)

        return {
            "message": f'File uploaded successfully',
            "s3_url": f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        }
    
    except HTTPException as http_exp:
        raise http_exp
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