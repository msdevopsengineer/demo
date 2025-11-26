from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class AuthEvent(Base):
    __tablename__ = "auth_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    authenticator_id = Column(UUID(as_uuid=True), ForeignKey("authenticators.id"), nullable=True)
    event_type = Column(String, nullable=False) # provision, verify_success, verify_fail, etc.
    detail = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
