from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.resume_processor import ResumeProcessor
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process")
async def process_resume(
    resume: UploadFile = File(...),  
    job_description: str = Form(...) 
):
    """
    Process resume PDF with job description
    Args:
        resume: PDF file (required)
        job_description: Text input (required)
    """
    try:
        # Validate inputs
        if not resume.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        if not job_description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty"
            )

        pdf_bytes = await resume.read()
        
        processor = ResumeProcessor()
        result = await processor.process_and_analyze_resume(pdf_bytes, job_description)

        print(f"Processing result: {result}")

        if result.get("status") == "success":
            return {
                "success": True,
                "filename": resume.filename,
                "page_count": len(result["original_resume"]["pages"]),
                "analysis": result["analysis"]
            }
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": result.get("error", "Unknown error"),
                    "suggestion": result.get("suggestion", "Check your API key and network connection")
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Resume processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing error: {str(e)}"
        )