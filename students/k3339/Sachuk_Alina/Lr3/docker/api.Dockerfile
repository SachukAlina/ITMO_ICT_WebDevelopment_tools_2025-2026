FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /service

COPY Lr1/requirements.txt /tmp/requirements-lr1.txt
COPY Lr3/requirements-api.txt /tmp/requirements-api.txt
RUN pip install --no-cache-dir -r /tmp/requirements-lr1.txt -r /tmp/requirements-api.txt

COPY Lr1/app ./app
COPY Lr1/migrations ./migrations
COPY Lr1/alembic.ini ./alembic.ini
COPY Lr3/gateway ./gateway
COPY Lr3/shared ./shared

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn gateway.main:app --host 0.0.0.0 --port 8000"]
