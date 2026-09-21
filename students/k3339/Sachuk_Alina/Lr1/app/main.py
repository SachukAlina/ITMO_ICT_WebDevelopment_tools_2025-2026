from fastapi import FastAPI

from app.config import settings
from app.routers import auth, authors, books, exchanges, library

app = FastAPI(
    title=settings.app_name,
    description="API для обмена книгами.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(authors.router)
app.include_router(books.router)
app.include_router(library.router)
app.include_router(exchanges.router)


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    return {"message": "BookCrossing API"}


@app.get("/health", tags=["service"])
def health() -> dict[str, str]:
    return {"status": "ok"}
