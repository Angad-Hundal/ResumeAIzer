from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_parsing import PdfParsing
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    print("REACHED TILL ROUTER UPLOAD PDF")
    logger.info(f"Received file: {file.filename}")

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    try:
        content = await file.read()
        
        # Validate file size (e.g., 10MB limit)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="File too large (max 10MB)"
            )
        
        parser = PdfParsing()
        result = parser.parse(content)
        
        logger.info(f"Processed PDF: {file.filename}")
        
        return {
            "filename": file.filename,
            "results": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )