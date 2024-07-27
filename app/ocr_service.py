from fastapi import APIRouter, UploadFile, File, HTTPException
import boto3
import pytesseract
from PIL import Image
import io
import os
import time
from config.config import Config

router = APIRouter()
config = Config()

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=config.SECRET_KEY,
        aws_secret_access_key=config.SECRET_KEY,
        region_name=config.S3_REGION
    )

@router.post("/ocr")
async def ocr_service(file: UploadFile = File(...)):
    try:
        # Ensure file is an image
        if not file.content_type.startswith('image'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        image = Image.open(io.BytesIO(await file.read()))
        text = pytesseract.image_to_string(image)

        # Initialize S3 client
        s3_client = get_s3_client()

        # Generate a unique file name for S3
        s3_key = f'ocr_results/{file.filename}_{int(time.time())}.txt'

        # Save the result to S3 with SSE-KMS encryption
        s3_client.put_object(
            Bucket=config.S3_BUCKET,
            Key=s3_key,
            Body=text,
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=config.KMS_KEY_ID
        )

        return {"text": text, "s3_key": s3_key}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
