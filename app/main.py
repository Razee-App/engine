import os
import sys
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.v1.endpoints import document_service, ocr_service, video_service
from app.core.config import Config

# Debug prints
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Load environment variables
load_dotenv()

# Create the Config instance
config = Config()
print("Configuration Loaded:")
print(config)

app = FastAPI()

# Include routers
app.include_router(document_service.router, prefix="/api/v1", tags=["Document Service"])
app.include_router(ocr_service.router, prefix="/api/v1", tags=["OCR Service"])
app.include_router(video_service.router, prefix="/api/v1", tags=["Video Service"])
app.include_router(video_service.router, prefix="/api/v1", tags=["Test Service"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Razee AI Engine Microservices"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
