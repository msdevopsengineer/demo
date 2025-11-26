from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=True)
    # In a real app, we'd have hashed_password, etc.
    # Here we assume the integrator manages identity and just links to this user_id.
