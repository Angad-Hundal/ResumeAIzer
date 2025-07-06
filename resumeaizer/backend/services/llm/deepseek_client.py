import httpx
import os
import logging
from typing import Optional
from .models import DeepSeekRequest, DeepSeekResponse
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self):
        self.api_base = "https://api.deepseek.com/v1"
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key not configured")

    async def analyze_resume(
        self,
        resume_data: Dict[str, Any],
        job_description: str
    ) -> DeepSeekResponse:
        """Send resume analysis request to DeepSeek API"""
        payload = DeepSeekRequest(
            resume_data=resume_data,
            job_description=job_description
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json=payload.dict(),
                    headers=headers
                )
                response.raise_for_status()
                json_response = response.json()
                
                return DeepSeekResponse(
                    success=True,
                    data=self._parse_response(json_response),
                    usage=json_response.get("usage")
                )
                
        except httpx.HTTPStatusError as e:
            error_msg = f"API error: {e.response.text}"
            logger.error(error_msg)
            return DeepSeekResponse(
                success=False,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(error_msg)
            return DeepSeekResponse(
                success=False,
                error=error_msg
            )

    def _parse_response(self, response: Dict) -> Dict[str, Any]:
        """Parse and validate API response"""
        try:
            content = response["choices"][0]["message"]["content"]
            return content if isinstance(content, dict) else {"raw": content}
        except (KeyError, AttributeError) as e:
            logger.warning(f"Failed to parse response: {str(e)}")
            return {"raw_response": response}