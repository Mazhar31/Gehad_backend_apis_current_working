from fastapi import HTTPException as FastAPIHTTPException
from typing import Any, Dict, Optional


class HTTPException(FastAPIHTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)