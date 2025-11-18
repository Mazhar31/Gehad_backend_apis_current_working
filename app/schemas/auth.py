from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[str] = None  # "admin" or "user"


class TwoFactorSetup(BaseModel):
    secret: str
    qr_code: str


class TwoFactorVerify(BaseModel):
    token: str