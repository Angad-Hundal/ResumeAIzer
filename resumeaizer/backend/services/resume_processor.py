from dotenv import load_dotenv
from typing import Dict, Any
from pathlib import Path
from services.llm.openai_client import OpenAIClient
import logging
import base64
from io import BytesIO

env_path = Path(__file__).resolve().parents[2] / '.env'
print(f"Loading environment variables from {env_path}")
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class ResumeProcessor:
    def __init__(self):
        self.llm_client = OpenAIClient()

    async def analyze_resume(self, pdf_bytes: bytes, job_description: str) -> Dict[str, Any]:
        """Main processing pipeline using OpenAIClient and PromptTemplates"""

        try:
            response = await self.llm_client.analyze_resume_with_llm(
                pdf_bytes=pdf_bytes,
                job_description=job_description
            )

            if not response.success:
                return {
                    "status": "error",
                    "error": response.error or "Unknown error from OpenAI API",
                    "suggestion": "Check your API key, network connection, or API usage limits"
                }

            analysis = response.data.get("analysis", {}) if response.data else {}
            updated_resume_base64 = response.data.get("updated_resume", None)

            if updated_resume_base64:
                updated_resume = self._decode_base64_pdf(updated_resume_base64)
            else:
                updated_resume = None

            return {
                "status": "success",
                "analysis": analysis,
                "updated_resume": updated_resume  # Include the updated resume in the response
            }
        except ValueError as e:
            return {
                "status": "error",
                "error": str(e),
                "suggestion": "Check your API key and network connection"
            }
        except Exception as e:
            logger.exception(f"Resume processing failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "suggestion": "Unexpected error occurred"
            }
        
    def _decode_base64_pdf(self, base64_pdf: str) -> BytesIO:
        """Decode the base64-encoded PDF and return it as a BytesIO object"""
        try:
            # Decode the base64 string to bytes
            pdf_bytes = base64.b64decode(base64_pdf)
            return BytesIO(pdf_bytes)  # Return as BytesIO object for further processing
        except Exception as e:
            logger.error(f"Error decoding base64 PDF: {str(e)}")
            raise ValueError("Failed to decode the base64 PDF.")