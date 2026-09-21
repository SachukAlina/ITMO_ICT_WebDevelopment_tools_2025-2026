from collections.abc import AsyncGenerator
from typing import Annotated

import httpx
from app.security import CurrentUser
from celery import Celery
from celery.exceptions import BackendError
from fastapi import APIRouter, Depends, HTTPException, status
from kombu.exceptions import OperationalError as BrokerConnectionError
from pydantic import BaseModel, HttpUrl
from redis.exceptions import RedisError

from gateway.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, PARSER_SERVICE_URL
from shared.validation import validate_book_url


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


class TaskSubmitted(BaseModel):
    task_id: str
    status: str


class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: ParseResponse | None = None
    error: str | None = None


async def get_parser_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(base_url=PARSER_SERVICE_URL, timeout=30) as client:
        yield client


ParserClient = Annotated[httpx.AsyncClient, Depends(get_parser_client)]
router = APIRouter(prefix="/parser", tags=["parser"])
celery_client = Celery(
    "book_parser_client",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)


@router.post("/parse", response_model=ParseResponse)
async def start_direct_parsing(
    payload: ParseRequest,
    client: ParserClient,
    _: CurrentUser,
) -> ParseResponse:
    url = _validated_url(payload)
    try:
        response = await client.post("/parse", json={"url": url})
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        detail = error.response.text or "Parser rejected the request"
        raise HTTPException(error.response.status_code, detail=detail) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Parser service is unavailable: {error}",
        ) from error
    return ParseResponse.model_validate(response.json())


@router.post(
    "/tasks", response_model=TaskSubmitted, status_code=status.HTTP_202_ACCEPTED
)
def enqueue_parsing(payload: ParseRequest, _: CurrentUser) -> TaskSubmitted:
    url = _validated_url(payload)
    try:
        task = celery_client.send_task("parse_book", args=[url])
    except (BrokerConnectionError, RedisError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task queue is unavailable",
        ) from error
    return TaskSubmitted(task_id=task.id, status="queued")


@router.get("/tasks/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str, _: CurrentUser) -> TaskStatus:
    try:
        task = celery_client.AsyncResult(task_id)
        if task.successful():
            return TaskStatus(
                task_id=task_id,
                status=task.status.lower(),
                result=ParseResponse.model_validate(task.result),
            )
        if task.failed():
            return TaskStatus(
                task_id=task_id,
                status=task.status.lower(),
                error=str(task.result),
            )
        return TaskStatus(task_id=task_id, status=task.status.lower())
    except (BackendError, RedisError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task result backend is unavailable",
        ) from error


def _validated_url(payload: ParseRequest) -> str:
    try:
        return validate_book_url(str(payload.url))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
