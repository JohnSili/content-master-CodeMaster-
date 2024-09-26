from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router as api_router
from app.db.database import engine, Base
from app.models import author, article
from app.models.author import Author as AuthorModel
from app.models.author import TextTone
from app.models.article import Article as ArticleModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ContentMaster API")

app.mount("/static", StaticFiles(directory="ui/static"), name="static")
templates = Jinja2Templates(directory="ui/templates")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/author-management")
async def author_management(request: Request):
    return templates.TemplateResponse("author_management.html", {"request": request})

@app.get("/article-generation")
async def article_generation(request: Request):
    return templates.TemplateResponse("article_generation.html", {"request": request})

@app.get("/saved-articles")
async def saved_articles(request: Request):
    return templates.TemplateResponse("saved_articles.html", {"request": request})

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        def check_tables(connection):
            with Session(connection) as session:
                insp = inspect(session.connection())
                existing_tables = insp.get_table_names()
                print(f"Existing tables: {existing_tables}")
                
                if 'articles' not in existing_tables:
                    print("WARNING: 'articles' table does not exist!")
                
                # Check if there are any articles
                result = session.execute(text("SELECT COUNT(*) FROM articles"))
                count = result.scalar()
                if count == 0:
                    print("No articles found. Adding a test article.")
                    session.execute(text("""
                        INSERT INTO articles (topic, content, style, length)
                        VALUES (:topic, :content, :style, :length)
                    """), {
                        "topic": "Test Article",
                        "content": "This is a test article content.",
                        "style": "formal",
                        "length": 100
                    })
                    session.commit()
                    print("Added test article")
                else:
                    print(f"Found {count} articles")

        await conn.run_sync(check_tables)




    
    # async with AsyncSession(engine) as session:
    #     test_author = AuthorModel(
    #         name="Test Author",
    #         description="This is a test author",
    #         specialty="Testing",
    #         keywords="test, author",
    #         phrases="test phrase",
    #         text_tone=TextTone.formal
    #     )
    #     session.add(test_author)
    #     await session.commit()

    print("Startup function completed")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)