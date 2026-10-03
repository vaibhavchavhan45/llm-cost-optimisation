# FastAPI entry point.

from fastapi import FastAPI, Request

from api.router_json_routes import router as json_router
from api.router_text_routes import router as text_router
from middleware.error_handler import generic_exception_handler

app = FastAPI(title="LLM Cost Optimization Router API")

app.include_router(json_router)
app.include_router(text_router)

app.add_exception_handler(Exception, generic_exception_handler)


@app.api_route("/", methods=["GET", "HEAD"])
def root(request: Request):
    return {
        "message": "Welcome to the API. Visit the link below to try it out.",
        "docs_url": f"{request.base_url}docs"
    }