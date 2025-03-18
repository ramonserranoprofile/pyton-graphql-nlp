from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    # Generar el esquema OpenAPI predeterminado
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

    # Agregar la configuración de seguridad JWT
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "token",
                    "scopes": {},
                }
            },
        }
    }

    # Especificar que las rutas protegidas requieren autenticación
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]

    # Guardar el esquema personalizado en la aplicación
    app.openapi_schema = openapi_schema
    return app.openapi_schema
