from sqlalchemy import Column, Integer, String, Enum
from app.db.database import Base
from sqlalchemy.orm import relationship
import enum

class TextTone(enum.Enum):
    formal = "formal"
    informal = "informal"

class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    specialty = Column(String)
    keywords = Column(String)
    phrases = Column(String)
    text_tone = Column(Enum(TextTone))
    articles = relationship("Article", back_populates="author")

    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "specialty": self.specialty,
            "keywords": self.keywords,
            "phrases": self.phrases,
            "text_tone": self.text_tone.value if self.text_tone else None
        }

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}', text_tone='{self.text_tone}')>"