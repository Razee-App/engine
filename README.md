Got it! Here's a README tailored specifically for the microservices used in the Razee application.

---

# Razee Microservices

## Overview

This project consists of Flask-based microservices designed for the Razee application. It includes services for Optical Character Recognition (OCR), video-to-text conversion, and document processing using LangChain. AWS S3 is used for document storage, and the services are modular to support the needs of the Razee platform.

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

```
flask
boto3
langchain
openai
pinecone-client
pytesseract
moviepy
pandas
```

Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR

```bash
brew install tesseract
```

## Configuration

### AWS S3

Ensure your AWS credentials are configured. You can set them up using the AWS CLI:

```bash
aws configure
```

### Environment Variables

Create a `.env` file in the root directory and add your environment variables:

```
SECRET_KEY=your_secret_key
S3_BUCKET=your_bucket_name
LANGCHAIN_API_KEY=your_langchain_api_key
```

## Running the Application

Start the Flask application with:

```bash
python run.py
```

The application will be accessible at `http://127.0.0.1:5000`.

## Endpoints

### OCR Service

- **Endpoint**: `/api/ocr`
- **Method**: `POST`
- **Description**: Convert images to text.
- **Form-data Parameters**:
  - `file`: The image file to process.

### Video-to-Text Service

- **Endpoint**: `/api/video-to-text`
- **Method**: `POST`
- **Description**: Convert video streams to text.
- **Form-data Parameters**:
  - `file`: The video file to process.

### Document Service

- **Endpoint**: `/api/upload-document`
- **Method**: `POST`
- **Description**: Upload and process documents.
- **Form-data Parameters**:
  - `file`: The document file to upload.

## File Structure

- `app/`
  - `__init__.py`: Initialize Flask application and register blueprints.
  - `ocr_service.py`: Service for OCR processing.
  - `video_service.py`: Service for video-to-text conversion.
  - `document_service.py`: Service for document processing and annotation.
  - `utils.py`: Utility functions.
- `config/`
  - `config.py`: Configuration settings.
- `models/`
  - `__init__.py`: Initialize model components.
  - `langchain_model.py`: LangChain model integration.
  - `pinecone_model.py`: Pinecone model integration.
- `run.py`: Entry point to start the Flask application.
- `.gitignore`: Git ignore configuration.
- `requirements.txt`: List of Python dependencies.
- `.env`: Environment variables configuration.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.


## Contact

For any questions or issues related to the Razee application, please contact nader@razee.app.

