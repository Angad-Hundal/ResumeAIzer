import httpx
import os
import logging
import json
from typing import Dict, Any
from .models import OpenAIResponse 
from .prompt_template import PromptTemplates

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.api_base = "https://models.github.ai/inference"
        self.model = "openai/gpt-4.1"
        self.api_key = os.getenv("GITHUB_TOKEN")
        if not self.api_key:
            raise ValueError("GitHub API key not configured")

    async def analyze_resume(
        self,
        resume_data: Dict[str, Any],
        job_description: str
    ) -> OpenAIResponse: 
        """Send resume analysis request to GitHub-hosted OpenAI model"""
        prompt = PromptTemplates.get_analysis_template(resume_data, job_description)
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            print("HEADERS:", headers)
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers
                )
                json_response = response.json()
                print("Response JSON:", json.dumps(json_response, indent=2))

                if response.status_code == 200:
                    parsed = self._parse_response(json_response)
                    return OpenAIResponse( 
                        success=True,
                        data=parsed,
                        usage=json_response.get("usage")
                    )
                else:
                    error_msg = f"API error: {json_response}"
                    logger.error(error_msg)
                    return OpenAIResponse(success=False, error=error_msg)
        except httpx.HTTPStatusError as e:
            error_msg = f"API error: {e.response.text}"
            logger.error(error_msg)
            return OpenAIResponse(success=False, error=error_msg)
        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            logger.error(error_msg)
            return OpenAIResponse(success=False, error=error_msg)

    def _parse_response(self, response: Dict) -> Dict[str, Any]:
        """Parse and validate API response, extracting JSON from string if needed"""
        try:
            content = response["choices"][0]["message"]["content"]
            if isinstance(content, str):
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
