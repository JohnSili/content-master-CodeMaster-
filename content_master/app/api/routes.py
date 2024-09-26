from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from app.db.database import get_db
from app.models.author import Author as AuthorModel, TextTone
from app.models.article import Article as ArticleModel
from pydantic import BaseModel, Field
from app.services.text_generator import text_generator
from app.services.news_service import news_service
from typing import List, Optional
from enum import Enum
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from app.services.text_analysis import analyze_text

router = APIRouter()

class TextTone(str, Enum):
    formal = "formal"
    informal = "informal"

class ArticleAnalytics(BaseModel):
    statistics: dict
    keywords: List[tuple]
    word_cloud: str

class AuthorCreate(BaseModel):
    name: str
    description: str
    specialty: str
    keywords: str = Field(default="")
    phrases: str = Field(default="")
    text_tone: TextTone

class AuthorResponse(AuthorCreate):
    id: int

    class Config:
        from_attributes = True

class ArticleBase(BaseModel):
    topic: str
    content: str
    style: str
    length: int
    author_id: Optional[int] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    id: int
    author_name: Optional[str] = None

    class Config:
        from_attributes = True

class ArticleGeneration(BaseModel):
    topic: str
    length: int
    style: str
    author_id: Optional[int] = None
    model: str = "google/gemini-flash-8b-1.5-exp"

class ArticleUpdate(BaseModel):
    topic: Optional[str] = None
    content: Optional[str] = None
    style: Optional[str] = None
    length: Optional[int] = None
    author_id: Optional[int] = None

@router.post("/authors", response_model=AuthorResponse)
async def create_author(author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    try:
        author_data = author.dict()
        author_data['keywords'] = ','.join(author.keywords.split())
        author_data['phrases'] = ','.join(author.phrases.split())
        
        db_author = AuthorModel(**author_data)
        db.add(db_author)
        await db.commit()
        await db.refresh(db_author)
        return db_author
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/authors", response_model=List[AuthorResponse])
async def list_authors(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AuthorModel))
        authors = result.scalars().all()
        return authors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/authors/{author_id}", response_model=AuthorResponse)
async def read_author(author_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuthorModel).filter(AuthorModel.id == author_id))
    db_author = result.scalar_one_or_none()
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return db_author

@router.post("/generate-article")
async def generate_article(article: ArticleGeneration, db: AsyncSession = Depends(get_db)):
    try:
        author = None
        if article.author_id:
            result = await db.execute(select(AuthorModel).filter(AuthorModel.id == article.author_id))
            author = result.scalar_one_or_none()
            if not author:
                raise HTTPException(status_code=404, detail="Author not found")
        
        content = await text_generator.generate_article(
            topic=article.topic,
            length=article.length,
            style=article.style,
            author_profile=author.dict() if author else None,
            model=article.model
        )

        # Сохраняем сгенерированную статью в базе данных
        db_article = ArticleModel(
            topic=article.topic,
            content=content,
            style=article.style,
            length=article.length,
            author_id=article.author_id
        )
        db.add(db_article)
        await db.commit()
        await db.refresh(db_article)

        return {"id": db_article.id, "content": content}
    except Exception as e:
        print(f"Error in generate_article: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/available-models")
async def get_available_models():
    return {"models": text_generator.get_available_models()}

@router.put("/authors/{author_id}", response_model=AuthorResponse)
async def update_author(author_id: int, author: AuthorCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            update(AuthorModel).where(AuthorModel.id == author_id).values(**author.dict())
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Author not found")
        await db.commit()
        
        updated_author = await db.get(AuthorModel, author_id)
        return updated_author
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete("/authors/{author_id}", status_code=204)
async def delete_author(author_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(delete(AuthorModel).where(AuthorModel.id == author_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Author not found")
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/news")
async def get_news(category: str = "general", country: str = "us", page_size: int = 10):
    news = await news_service.get_top_headlines(category, country, page_size)
    return {"news": news}

@router.post("/articles", response_model=ArticleResponse)
async def create_article(article: ArticleCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_article = ArticleModel(**article.dict())
        db.add(db_article)
        await db.commit()
        await db.refresh(db_article)
        return ArticleResponse(
            id=db_article.id,
            topic=db_article.topic,
            content=db_article.content,
            style=db_article.style,
            length=db_article.length,
            author_id=db_article.author_id,
            author_name=db_article.author.name if db_article.author else None
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.put("/articles/{article_id}")
async def update_article(article_id: int, article_update: ArticleUpdate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(ArticleModel).filter(ArticleModel.id == article_id))
    db_article = result.scalar_one_or_none()
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    
    for key, value in article_update.dict(exclude_unset=True).items():
        setattr(db_article, key, value)
    
    await db.commit()
    await db.refresh(db_article)
    return db_article

@router.get("/articles", response_model=List[ArticleResponse])
async def list_articles(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(ArticleModel).options(selectinload(ArticleModel.author))
        )
        articles = result.scalars().all()
        return [
            ArticleResponse(
                id=article.id,
                topic=article.topic,
                content=article.content,
                style=article.style,
                length=article.length,
                author_id=article.author_id,
                author_name=article.author.name if article.author else None
            )
            for article in articles
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def read_article(article_id: int, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        select(ArticleModel).options(selectinload(ArticleModel.author)).filter(ArticleModel.id == article_id)
    )
    article = result.scalar_one_or_none()
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleResponse(
        id=article.id,
        topic=article.topic,
        content=article.content,
        style=article.style,
        length=article.length,
        author_id=article.author_id,
        author_name=article.author.name if article.author else None
    )

@router.delete("/articles/{article_id}", status_code=204)
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(delete(ArticleModel).where(ArticleModel.id == article_id))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Article not found")
        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/articles/{article_id}/analytics", response_model=ArticleAnalytics)
async def get_article_analytics(article_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(ArticleModel).filter(ArticleModel.id == article_id))
        article = result.scalar_one_or_none()
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        
        # Используйте функцию analyze_text для получения аналитики
        analytics = analyze_text(article.content)
        
        return ArticleAnalytics(
            statistics=analytics['statistics'],
            keywords=analytics['keywords'],
            word_cloud=analytics['word_cloud']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")