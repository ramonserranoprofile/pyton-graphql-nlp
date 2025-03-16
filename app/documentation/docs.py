from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    # Generar el esquema OpenAPI por defecto
    openapi_schema = get_openapi(
        title="Python GraphQL & DeepSeek NLP implementation API",
        version="1.0",
        description="This is a custom OpenAPI 3.0 documentation for the Challenge Python GraphQL & DeepSeek NLP implementation API.",
        routes=app.routes,
    )

    # Personalizar el esquema (opcional)
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    # Guardar el esquema personalizado en la aplicación
    app.openapi_schema = openapi_schema
    return app.openapi_schema
