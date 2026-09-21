from app.main import app

from gateway.parser_api import router as parser_router

app.include_router(parser_router)
