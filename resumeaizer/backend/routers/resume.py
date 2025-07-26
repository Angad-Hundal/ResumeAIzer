from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.resume_processor import ResumeProcessor
import logging
import base64

router = APIRouter()
logger = logging.getLogger(__name__)

PROVIDED_MODELS = ['github', 'huggingface']

@router.post("/process")
async def process_resume(
    resume: UploadFile = File(...),  
    job_description: str = Form(...),
    model: str = Form("github")
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
        
        if model not in PROVIDED_MODELS:
            raise HTTPException(
                status_code=400,
                detail="Invalid model specified. Choose 'github' or 'huggingface'."
            )

        pdf_bytes = await resume.read()
        processor = ResumeProcessor()
        result = await processor.analyze_resume(pdf_bytes, job_description, model)

        print(f"Processing result: {result}")
        if result.get("status") == "success":
            updated_resume = result.get("updated_resume", None)
            if updated_resume:
                updated_resume_base64 = base64.b64encode(updated_resume.getvalue()).decode('utf-8')

                return {
                    "success": True,
                    "filename": resume.filename,
                    "page_count": len(result["analysis"].get("pages", [])),
                    "analysis": result["analysis"],
                    "updated_resume": updated_resume_base64 
                }
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Updated resume not returned from analysis"
                )
        else:
            # If the result failed, return an error
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