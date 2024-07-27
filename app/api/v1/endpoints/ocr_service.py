from fastapi import APIRouter, UploadFile, File, HTTPException
import pytesseract
from PIL import Image
import io

router = APIRouter()

@router.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    try:
        # Ensure file is an image
        if not file.content_type.startswith('image'):
            raise HTTPException(status_code=400, detail="Invalid file type")

        image = Image.open(io.BytesIO(await file.read()))
        text = pytesseract.image_to_string(image)
        return {"text": text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
