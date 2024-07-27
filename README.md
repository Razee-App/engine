# Razee AI Engine - Microservices

## Overview

This project consists of FastAPI-based microservices designed for the Razee application. It includes services for Optical Character Recognition (OCR), video-to-text conversion, and document processing using LangChain. AWS S3 is used for document storage, and the services are modular to support the needs of the Razee platform.

## Features

- **OCR Service**: Convert images to text using Tesseract OCR.
- **Video-to-Text Service**: Extract text from video streams.
- **Document Service**: Process and annotate documents using LangChain and store them in AWS S3.
- **Modular Architecture**: Easily extend and add new services as needed for Razee.

## Prerequisites

- Python 3.7 or higher
- AWS account with S3 bucket configured
- Tesseract OCR installed
- LangChain API key (if using specific models)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/razee_microservices.git
cd razee_microservices
```

### 2. Set Up a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following content:

```plaintext
fastapi==0.68.2
uvicorn==0.15.0
python-dotenv==0.19.0
boto3==1.18.0
langchain==0.2.0
langchain-community==0.2.0
pytesseract==0.3.7
Pillow==8.0.0
moviepy==1.0.3
speechrecognition==3.8.1
pytest==6.2.4
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

```bash
# On macOS using Homebrew
brew install tesseract

# On Ubuntu
sudo apt-get install tesseract-ocr

# On Windows
# Download the installer from https://github.com/UB-Mannheim/tesseract/wiki
# and follow the installation instructions
```

## Configuration

### AWS S3

Ensure your AWS credentials are configured. You can set them up using the AWS CLI:

```bash
aws configure
```

### Environment Variables

Create a `.env` file in the root directory and add your environment variables:

```plaintext
SECRET_KEY=your_secret_key
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
S3_REGION=your_s3_region
S3_BUCKET=your_s3_bucket_name
KMS_KEY_ID=your_kms_key_id
```

## Running the Application

Start the FastAPI application with:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The application will be accessible at `http://127.0.0.1:8000`.

## Endpoints

### OCR Service

- **Endpoint**: `/api/v1/ocr`
- **Method**: `POST`
- **Description**: Convert images to text.
- **Form-data Parameters**:
  - `file`: The image file to process.

### Video-to-Text Service

- **Endpoint**: `/api/v1/video-to-text`
- **Method**: `POST`
- **Description**: Convert video streams to text.
- **Form-data Parameters**:
  - `file`: The video file to process.

### Document Service

- **Endpoint**: `/api/v1/upload-document`
- **Method**: `POST`
- **Description**: Upload and process documents.
- **Form-data Parameters**:
  - `file`: The document file to upload.

## Testing

To run tests, use `pytest`. Make sure your virtual environment is activated.

```bash
pytest app/tests/test_upload.py
```

You can suppress deprecation warnings during testing by creating a `pytest.ini` file in the root of your project with the following content:

**pytest.ini**:

```ini
[pytest]
filterwarnings =
    ignore::DeprecationWarning
```

## Directory Structure

```
your_project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── document_service.py
│   │   │   │   ├── ocr_service.py
│   │   │   │   ├── video_service.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_service.py
│   │   ├── ocr_service.py
│   │   ├── video_service.py
│   ├── crud/
│   │   ├── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_upload.py
│   ├── utils/
│   │   ├── __init__.py
├── .env
├── .gitignore
├── Dockerfile
├── requirements.txt
├── README.md
├── setup.py
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Known Issues

### macOS Pydantic Core Compatibility

Users on macOS may encounter issues with the `pydantic_core` package due to architecture incompatibility. If you encounter errors related to `pydantic_core`, try the following steps:

1. Remove the existing virtual environment:
   ```bash
   deactivate
   rm -rf venv
   ```

2. Create a new virtual environment ensuring the correct architecture:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Rust for building some packages:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Reinstall `pydantic_core` with the correct architecture:
   ```bash
   pip install pydantic-core==2.20.1 --force-reinstall --no-binary :all:
   ```

## Contact

For any questions or issues related to the Razee application, please contact nader@razee.app.