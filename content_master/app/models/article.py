# from sqlalchemy import Column, Integer, String, Text, ForeignKey
# from sqlalchemy.orm import relationship
# from app.db.database import Base

# class Article(Base):
#     __tablename__ = "articles"

#     id = Column(Integer, primary_key=True, index=True)
#     topic = Column(String, index=True)
#     content = Column(Text)
#     style = Column(String)
#     length = Column(Integer)
#     author_id = Column(Integer, ForeignKey("authors.id"))

#     author = relationship("Author", back_populates="articles")

#     @property
#     def author_name(self):
#         return self.author.name if self.author else None
    
#     def dict(self):
#         return {
#             "id": self.id,
#             "topic": self.topic,
#             "content": self.content,
#             "style": self.style,
#             "length": self.length,
#             "author_id": self.author_id
#         }

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    content = Column(Text)
    style = Column(String)
    length = Column(Integer)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)

    author = relationship("Author", back_populates="articles")

    # def __dict__(self):
    #     return {
    #         "id": self.id,
    #         "topic": self.topic,
    #         "content": self.content,
    #         "style": self.style,
    #         "length": self.length,
    #         "author_id": self.author_id,
    #         "author_name": self.author.name if self.author else None
    #     }