from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    # Generate default OpenAPI Scheme
    openapi_schema = get_openapi(
        title="Python GraphQL & DeepSeek NLP implementation API",
        version="1.0",
        description="This is a custom OpenAPI 3.0 documentation for the Challenge Python GraphQL & DeepSeek NLP implementation API.",
        routes=app.routes,
    )

    # Personalize Scheme (optional)
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    # save custom Scheme in the app
    app.openapi_schema = openapi_schema
    return app.openapi_schema
