import os
from dotenv import load_dotenv
import httpx
from typing import Dict, Any
import json
from services.llm.prompt_template import PromptTemplates
from pathlib import Path

env_path = Path(__file__).resolve().parents[2] / '.env'
print(f"Loading environment variables from {env_path}")
load_dotenv(env_path)

import logging
logger = logging.getLogger(__name__)

class ResumeProcessor:
    def __init__(self):
        self.api_key = self._validate_key()
        self.timeout = float(os.getenv("API_TIMEOUT", "30.0"))
        self.base_url = "https://api.deepseek.com/v1"

    def _validate_key(self) -> str:
        """Validate and return the API key"""
        key = os.getenv("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError(
                "DeepSeek API key not found. "
                "Please set DEEPSEEK_API_KEY in .env file"
            )
        return key

    async def analyze_with_llm(self, prompt: str) -> Dict[str, Any]:
        """Send structured prompt to LLM with secure headers"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Environment": os.getenv("ENVIRONMENT", "development")
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return self._parse_response(response.json())
                
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API request failed: {e.response.text}")
        except Exception as e:
            raise ValueError(f"Connection error: {str(e)}")

    def _parse_response(self, response: Dict) -> Dict[str, Any]:
        """Safely parse and validate LLM response"""
        try:
            content = response['choices'][0]['message']['content']
            if isinstance(content, str):
                if content.startswith('```json'):
                    content = content[7:-3]  # Remove markdown code fences
                return json.loads(content)
            return content
        except (KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid API response: {str(e)}")

    async def process_resume(self, pdf_bytes: bytes, job_description: str) -> Dict[str, Any]:
        """Main processing pipeline with error handling"""
        from services.pdf_parser import PdfParser
        
        try:
            # Parse PDF
            parser = PdfParser()
            logger.info("Parsing PDF content")
            parsed_data = parser.parse_with_layout(pdf_bytes)
            
            # Generate prompt
            prompt = PromptTemplates.get_analysis_template(
                resume_data=parsed_data,
                job_description=job_description
            )
            
            # Get analysis
            analysis = await self.analyze_with_llm(prompt)
            
            return {
                "status": "success",
                "analysis": analysis.get("analysis", {}),
                "metadata": parsed_data.get("metadata", {})
            }
            
        except ValueError as e:
            return {
                "status": "error",
                "error": str(e),
                "suggestion": "Check your API key and network connection"
            }