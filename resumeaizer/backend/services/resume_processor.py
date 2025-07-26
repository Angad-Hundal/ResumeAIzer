from dotenv import load_dotenv
from typing import Dict, Any
from pathlib import Path
from services.llm.openai_client import OpenAIClient
import logging
import base64
from io import BytesIO
from pdf_parser import extract_text_from_pdf
from resumeaizer.backend.services.hugging_face.hugging_face_resume_analyzer import HuggingFaceResumeAnalyzer

env_path = Path(__file__).resolve().parents[2] / '.env'
print(f"Loading environment variables from {env_path}")
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class ResumeProcessor:
    def __init__(self):
        self.hugging_face_analyzer = HuggingFaceResumeAnalyzer()

    async def analyze_resume(self, pdf_bytes: bytes, job_description: str) -> Dict[str, Any]:
        """Main processing pipeline"""
        try:
            extracted_text = extract_text_from_pdf(pdf_bytes)
            
            result = await self.analyzer.process_resume(
                resume_text=extracted_text,
                job_description=job_description
            )
            return result
        
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }