from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.resume_processor import ResumeProcessor
import logging
from fastapi import status

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
        model: Processing model to use ('github' or 'huggingface')
    Returns:
        JSON response with analysis results or error details
    """
    try:
        if not resume.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Only PDF files are allowed",
                    "error_type": "file_validation",
                    "success": False
                }
            )
        
        if not job_description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Job description cannot be empty",
                    "error_type": "input_validation",
                    "success": False
                }
            )
        
        if model not in PROVIDED_MODELS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid model specified. Choose 'github' or 'huggingface'.",
                    "error_type": "model_validation",
                    "success": False
                }
            )

        pdf_bytes = await resume.read()
        processor = ResumeProcessor()
        result = await processor.analyze_resume(pdf_bytes, job_description, model)

        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY if result.get("error_type") == "input_validation" 
                else status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": result.get("message", "Unknown error"),
                    "error_type": result.get("error_type", "processing_error"),
                    "success": False
                }
            )

        return {
            "success": True,
            "filename": resume.filename,
            "analysis": result.get("analysis", {}),
            "critique": result.get("critique", ""),
            "market_trends": result.get("market_trends", ""),
            "iterations": result.get("iterations", 0),
            "satisfaction_score": result.get("satisfaction_score", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Resume processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "error_type": "unexpected_error",
                "success": False
            }
        )