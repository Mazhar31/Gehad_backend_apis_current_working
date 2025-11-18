from pydantic import BaseModel
from typing import Any, Optional, List


class ResponseModel(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    message: str = "Success"
    errors: List[str] = []