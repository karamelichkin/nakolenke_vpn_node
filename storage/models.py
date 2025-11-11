from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base


class VPNInterface(Base):
    __tablename__ = "vpn_interfaces"

    id = Column(Integer, primary_key=True, index=True)
    external_user_id = Column(String(255), nullable=False, index=True)
    interface_name = Column(String(50), unique=True, nullable=False)
    vpn_type = Column(String(20), nullable=False)
    status = Column(String(20), default="down")
    config = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
