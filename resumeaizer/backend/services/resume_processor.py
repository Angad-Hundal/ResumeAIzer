import os
from dotenv import load_dotenv
from typing import Dict, Any
from pathlib import Path
from services.llm.openai_client import OpenAIClient
import logging

env_path = Path(__file__).resolve().parents[2] / '.env'
print(f"Loading environment variables from {env_path}")
load_dotenv(env_path)

logger = logging.getLogger(__name__)

class ResumeProcessor:
    def __init__(self):
        self.llm_client = OpenAIClient()

    async def process_and_analyze_resume(self, pdf_bytes: bytes, job_description: str) -> Dict[str, Any]:
        """Main processing pipeline using OpenAIClient and PromptTemplates"""
        from services.pdf_parser import PdfParser

        try:
            parser = PdfParser()
            logger.info("Parsing PDF content")
            parsed_data = parser.parse_with_layout(pdf_bytes)

            response = await self.llm_client.analyze_resume(
                resume_data=parsed_data,
                job_description=job_description
            )

            if not response.success:
                return {
                    "status": "error",
                    "error": response.error or "Unknown error from OpenAI API",
                    "suggestion": "Check your API key, network connection, or API usage limits"
                }

            analysis = response.data.get("analysis", {}) if response.data else {}

            return {
                "status": "success",
                "original_resume": parsed_data,
                "analysis": analysis
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
