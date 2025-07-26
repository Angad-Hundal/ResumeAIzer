import os
import logging
import json
from typing import Dict, Any
from .models import OpenAIResponse
from .prompt_template import PromptTemplates
import base64
from io import BytesIO
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from services.pdf_parser import extract_text_from_pdf
import re

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.api_base = "https://models.github.ai/inference"  
        self.model = "openai/gpt-4.1"
        self.api_key = os.getenv("GITHUB_TOKEN")
        if not self.api_key:
            raise ValueError("GitHub API key not configured")
        
        # Initialize Azure ChatCompletionsClient
        self.client = ChatCompletionsClient(
            endpoint=self.api_base,
            credential=AzureKeyCredential(self.api_key)
        )

    async def analyze_resume_with_llm(self, pdf_bytes: bytes, job_description: str) -> OpenAIResponse:
        """Send resume analysis request to Azure-hosted OpenAI model"""

        resume_text = extract_text_from_pdf(pdf_bytes)

        
        prompt = PromptTemplates.get_analysis_template(job_description)
        full_prompt = f"{prompt}\n\nResume Content:\n{resume_text}"

        system_message = SystemMessage("Resume Analysis System")
        user_message = UserMessage(full_prompt)

        try:
            response = self.client.complete(
                messages=[system_message, user_message],
                temperature=0.3,
                top_p=1,
                model=self.model
            )

            print(f"Response from Azure LLM: {response}")
            return await self._handle_response(response)

        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return OpenAIResponse(success=False, error=str(e))

    async def _handle_response(self, response) -> OpenAIResponse:
        """Handle the response from the Azure LLM model"""
        try:
            content = response.choices[0].message.content
            print(f"Raw response content: {content}")

            if isinstance(content, str):
                if content.strip().startswith('```json'):
                    content = content.strip()[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                content = self.fix_base64_in_json(content)
                try:
                    print("INSIDE THE IF LOOPS")
                    parsed = json.loads(content)
                    if "updated_resume" in parsed.get("analysis", {}):
                        print("Found updated_resume in parsed response")
                        analysis = parsed.get("analysis", {})
                        base64_pdf = analysis.get("updated_resume", "")
                        decoded_pdf = base64.b64decode(base64_pdf)
                        parsed["updated_resume"] = BytesIO(decoded_pdf)
                    return OpenAIResponse(success=True, data=parsed)
                except json.JSONDecodeError:
                    return OpenAIResponse(success=False, error="Failed to decode JSON from response")
            return OpenAIResponse(success=True, data={"raw_content": content})
        except Exception as e:
            logger.warning(f"Failed to parse the response: {str(e)}")
            return OpenAIResponse(success=False, error=f"Failed to handle response: {str(e)}")
        

    def fix_base64_in_json(self, json_str: str) -> str:
        # Matches the base64 string associated with "updated_resume"
        pattern = r'("updated_resume"\s*:\s*")([\s\S]*?)(")'
        
        def replacer(match):
            key = match.group(1)
            value = match.group(2)
            end = match.group(3)
            clean_value = re.sub(r'\s+', '', value)
            return f'{key}{clean_value}{end}'

        return re.sub(pattern, replacer, json_str)
