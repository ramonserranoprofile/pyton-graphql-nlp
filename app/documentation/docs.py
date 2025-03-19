from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.auth.services.auth_service import LoginRequest


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    # Generar el esquema OpenAPI predeterminado
    openapi_schema = get_openapi(
        title="Python GraphQL & Gemini NLP implementation API",
        version="1.0",
        description="This is a custom OpenAPI 3.0 documentation for the Challenge Python GraphQL & Gemini NLP implementation API.",
        routes=app.routes,
    )

    # Agregar logo a la documentación
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    # Agregar seguridad JWT como Bearer Token
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    if "securitySchemes" not in openapi_schema["components"]:        
        # esquema oauth2
        openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] = {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/token",
                    "scopes": {}
                }
            }
        } 
        

    app.openapi_schema = openapi_schema  # Guardar el esquema en cache
    return app.openapi_schema


# Asignar la nueva función OpenAPI
app = FastAPI()
app.openapi = lambda: custom_openapi(app)