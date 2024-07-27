import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.ocr_service import router as ocr_router
from app.video_service import router as video_router
from app.document_service import router as document_router
from config.config import Config

# Load environment variables
load_dotenv()

app = FastAPI()

# Load configuration
config = Config()
print("Configuration Loaded:")
print(config)

# Include routers
app.include_router(ocr_router, prefix='/api', tags=["OCR Service"])
app.include_router(video_router, prefix='/api', tags=["Video-to-Text Service"])
app.include_router(document_router, prefix='/api', tags=["Document Service"])

@app.get("/")
async def root():
    return {"message": "Welcome to Razee AI Engine Microservices"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
