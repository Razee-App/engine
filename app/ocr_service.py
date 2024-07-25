from flask import Blueprint, request, jsonify, current_app
import boto3
import pytesseract
from PIL import Image
import io
import os

ocr_blueprint = Blueprint('ocr', __name__)

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['S3_REGION']
    )

@ocr_blueprint.route('/ocr', methods=['POST'])
def ocr_service():
    try:
        file = request.files['file']
        
        # Ensure file is an image
        if not file or not file.mimetype.startswith('image'):
            return jsonify({'error': 'Invalid file type'}), 400

        image = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(image)

        # Initialize S3 client within the request context
        s3_client = get_s3_client()

        # Generate a unique file name for S3
        s3_key = f'ocr_results/{file.filename}_{int(time.time())}.txt'
        
        # Save the result to S3 with SSE-KMS encryption
        s3_client.put_object(
            Bucket=current_app.config['S3_BUCKET'],
            Key=s3_key,
            Body=text,
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=current_app.config['KMS_KEY_ID']
        )

        return jsonify({'text': text, 's3_key': s3_key})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
