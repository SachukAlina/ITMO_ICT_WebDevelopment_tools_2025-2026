FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /service

COPY Lr2/requirements.txt /tmp/requirements-lr2.txt
COPY Lr3/requirements-parser.txt /tmp/requirements-parser.txt
RUN pip install --no-cache-dir -r /tmp/requirements-lr2.txt -r /tmp/requirements-parser.txt

COPY Lr2/parsers ./parsers
COPY Lr3/parser_service ./parser_service
COPY Lr3/shared ./shared
COPY Lr3/worker ./worker

RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8001
CMD ["uvicorn", "parser_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
