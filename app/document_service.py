from flask import Blueprint, request, jsonify, current_app
import boto3
from langchain.chains import LLMChain
from langchain.llms import OpenAI
import io

document_blueprint = Blueprint('document', __name__)

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['S3_REGION']
    )

def get_langchain():
    llm = OpenAI(model="text-davinci-003")  # Update model if needed
    return LLMChain(llm=llm)

@document_blueprint.route('/upload-document', methods=['POST'])
def upload_document():
    try:
        file = request.files['file']

        # Validate file type and size
        if not file or not file.mimetype.startswith('text'):
            return jsonify({'error': 'Invalid file type or empty file'}), 400

        s3_client = get_s3_client()
        bucket_name = current_app.config['S3_BUCKET']
        s3_key = f'documents/{file.filename}'  # Customize path as needed

        # Upload file to S3
        s3_client.upload_fileobj(file, bucket_name, s3_key)

        # Process document with LangChain
        file.seek(0)  # Move cursor to the start of the file
        langchain = get_langchain()
        text = langchain.run(file.read().decode('utf-8'))  # Ensure the file is read as a string

        # Optionally add text to document repository
        # Your code to add text to a repository

        return jsonify({'text': text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_blueprint.route('/test-upload', methods=['POST'])
def test_upload():
    try:
        file = request.files['file']
        bucket_name = current_app.config['S3_BUCKET']
        s3_key = f'test/{file.filename}'  # Use a specific path or filename for testing

        s3_client = get_s3_client()
        s3_client.upload_fileobj(file, bucket_name, s3_key)

        return jsonify({'message': f'File uploaded to {bucket_name}/{s3_key}'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_blueprint.route('/print-config', methods=['GET'])
def print_config():
    try:
        config = {
            'SECRET_KEY': current_app.config.get('SECRET_KEY'),
            'AWS_ACCESS_KEY_ID': current_app.config.get('AWS_ACCESS_KEY_ID'),
            'AWS_SECRET_ACCESS_KEY': current_app.config.get('AWS_SECRET_ACCESS_KEY'),
            'S3_REGION': current_app.config.get('S3_REGION'),
            'S3_BUCKET': current_app.config.get('S3_BUCKET'),
            'KMS_KEY_ID': current_app.config.get('KMS_KEY_ID')
        }
        return jsonify(config)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
