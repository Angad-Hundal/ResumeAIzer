import httpx
import os
import logging
from typing import Optional
from .models import DeepSeekResponse
from typing import Dict, Any
from .prompt_template import PromptTemplates
import json

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
        """Send resume analysis request to DeepSeek API using template prompt"""
        prompt = PromptTemplates.get_analysis_template(resume_data, job_description)
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            print("PAYLOAD: ", payload)  
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers
                )
                json_response = response.json()
                if response.status_code == 200:
                    parsed = self._parse_response(json_response)
                    return DeepSeekResponse(
                        success=True,
                        data=parsed,
                        usage=json_response.get("usage")
                    )
                else:
                    error_msg = f"API error: {json_response}"
                    logger.error(error_msg)
                    return DeepSeekResponse(
                        success=False,
                        error=error_msg
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
        """Parse and validate API response, extracting JSON from string if needed"""
        try:
            content = response["choices"][0]["message"]["content"]
            if isinstance(content, str):
                # Remove markdown code fences if present
                if content.strip().startswith('```json'):
                    content = content.strip()[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"raw": content}
            return content
        except (KeyError, AttributeError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse response: {str(e)}")
            return {"raw_response": response}