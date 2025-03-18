from fastapi import FastAPI, Depends
from pydantic import BaseModel
from app.data.routers.graphql_router import graphql_router
from app.data.routers.nlp_router import nlp_router
from app.auth.services.auth_service import auth_router, add_token_to_request, get_current_active_user
from app.documentation.docs import custom_openapi


# Crear la aplicación FastAPI
app = FastAPI(
    title="Python GraphQL & DeepSeek NLP implementation API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",    
)
# Modelo para la respuesta de la ruta raíz
class RootRequest(BaseModel):    
    message: str


# Ruta de inicio
@app.get(
    "/",
    dependencies=[Depends(get_current_active_user)],
    tags=["Root"],
    include_in_schema=True,
    response_description="Root Endpoint",
    response_model=RootRequest,
    summary="Root Endpoint",
)
def read_root():
    return {"message": "Hello, world!"}


# Aplicar el esquema OpenAPI personalizado
app.openapi = lambda: custom_openapi(app)

# Aplicar el middleware para agregar el token automáticamente
app.middleware("http")(add_token_to_request)

# Registrar los routers
app.include_router(graphql_router, prefix="/api")
app.include_router(nlp_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

# Ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
