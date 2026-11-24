from .minirag_base import SQLAlchemyBase
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, autoincrement=True)
    project_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    project_name = Column(String, nullable=False)
    project_description = Column(String)


    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True
    )

    assets = relationship("Asset", back_populates="project")
    chunks = relationship("DataChunk", back_populates="project")