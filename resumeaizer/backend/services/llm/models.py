from pydantic import BaseModel
from typing import Dict, Any, Optional

class DeepSeekRequest(BaseModel):
    resume_data: Dict[str, Any]
    job_description: str
    instructions: str = "Analyze this resume against the job description"
    temperature: float = 0.7
    max_tokens: int = 2000

class DeepSeekResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, int]] = None