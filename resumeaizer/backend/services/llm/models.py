from pydantic import BaseModel
from typing import Dict, Any, Optional

class DeepSeekResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None


class OpenAIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    usage: Optional[dict] = None
    error: Optional[str] = None
