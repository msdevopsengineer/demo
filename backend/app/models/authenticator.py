from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Integer, LargeBinary, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from app.core.database import Base

class AuthenticatorStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"

class Authenticator(Base):
    __tablename__ = "authenticators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    secret_encrypted = Column(LargeBinary, nullable=False)
    display_name = Column(String, nullable=True)
    issuer = Column(String, nullable=True)
    status = Column(String, default=AuthenticatorStatus.PENDING) # Stored as string for simplicity or use Enum
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    provision_token = Column(UUID(as_uuid=True), nullable=True)
    provision_token_expires_at = Column(DateTime, nullable=True)
    
    failed_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    backup_codes = relationship("BackupCode", back_populates="authenticator", cascade="all, delete-orphan")

class BackupCode(Base):
    __tablename__ = "backup_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    authenticator_id = Column(UUID(as_uuid=True), ForeignKey("authenticators.id"), nullable=False)
    code_hash = Column(String, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    authenticator = relationship("Authenticator", back_populates="backup_codes")
