from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import Session

Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields for all tables"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    attivo = Column(Boolean, default=True, nullable=False, index=True)

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name"""
        return cls.__name__.lower()

    def soft_delete(self, db: Session):
        """Soft delete by setting attivo to False"""
        self.attivo = False
        db.commit()

    def restore(self, db: Session):
        """Restore soft deleted record"""
        self.attivo = True
        db.commit()

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
