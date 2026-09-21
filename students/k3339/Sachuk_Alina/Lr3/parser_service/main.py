import requests
from fastapi import FastAPI, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, HttpUrl

from parser_service.service import parse_book


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    cover_url: str | None = None
    source_url: str
    price: str | None = None
    availability: str | None = None
    rating: str | None = None


app = FastAPI(title="Book parser service", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse", response_model=ParseResponse)
async def parse(payload: ParseRequest) -> ParseResponse:
    try:
        result = await run_in_threadpool(parse_book, str(payload.url))
    except requests.RequestException as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not download source page: {error}",
        ) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return ParseResponse.model_validate(result)
