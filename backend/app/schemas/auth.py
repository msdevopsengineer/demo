from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    user_id: Optional[str] = None # Integrator provided ID or we generate
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class AuthenticatorProvisionRequest(BaseModel):
    user_id: str
    display_name: Optional[str] = "User"
    issuer: Optional[str] = "CustomAuthenticator"

class AuthenticatorProvisionResponse(BaseModel):
    secret_base32: str
    otpauth_uri: str
    qr_svg: str
    provision_token: str
    expires_at: datetime

class VerifySetupRequest(BaseModel):
    provision_token: str
    code: str

class VerifyRequest(BaseModel):
    user_id: str
    code: str
    client_ip: Optional[str] = None

class VerifyResponse(BaseModel):
    verified: bool
    timestamp: Optional[datetime] = None
    error: Optional[str] = None
    retry_after_seconds: Optional[int] = None

class BackupCodeGenerateRequest(BaseModel):
    user_id: str

class BackupCodeResponse(BaseModel):
    backup_codes: List[str]

class BackupVerifyRequest(BaseModel):
    user_id: str
    backup_code: str

class DisableRequest(BaseModel):
    user_id: str
