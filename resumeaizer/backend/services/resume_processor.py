from dotenv import load_dotenv
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from services.pdf_parser import extract_text_from_pdf
from services.hugging_face.hugging_face_resume_analyzer import MultiModelResumeAnalyzer
import asyncio

# env_path = Path(__file__).resolve().parents[2] / '.env'
# load_dotenv(env_path)
logger = logging.getLogger(__name__)

class ResumeProcessor:
    def __init__(self):
        """Initialize with proper error handling"""
        try:
            self.analyzer = MultiModelResumeAnalyzer()
            logger.info("Resume processor initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize: {str(e)}")
            raise

    async def analyze_resume(self, pdf_bytes: bytes, job_description: str) -> Dict[str, Any]:
        """
        Process a resume PDF with comprehensive error handling
        
        Example Success Response:
        {
            "status": "success",
            "analysis": "...",
            "critique": "...", 
            "market_trends": "...",
            "iterations": 2,
            "satisfaction_score": 78.5
        }
        
        Example Error Response:
        {
            "status": "error",
            "message": "Invalid PDF format",
            "error_type": "input_validation"
        }
        """
        try:
            if not pdf_bytes:
                raise ValueError("No PDF content provided")
            if not job_description.strip():
                raise ValueError("Job description cannot be empty")

            text = await self._extract_text_safely(pdf_bytes)
            return await self.analyzer.process_resume(text, job_description)
            
        except ValueError as e:
            return self._format_error(str(e), "input_validation")
        except asyncio.TimeoutError:
            return self._format_error("Processing timed out", "timeout")
        except Exception as e:
            logger.exception("Unexpected error")
            return self._format_error(str(e), "processing_error")

    async def _extract_text_safely(self, pdf_bytes: bytes) -> str:
        """Extract text with validation"""
        text = extract_text_from_pdf(pdf_bytes)
        if not text.strip():
            raise ValueError("PDF contained no readable text")
        return text

    def _format_error(self, message: str, error_type: str) -> Dict[str, Any]:
        """Standard error response format"""
        return {
            "status": "error",
            "message": message,
            "error_type": error_type
        }