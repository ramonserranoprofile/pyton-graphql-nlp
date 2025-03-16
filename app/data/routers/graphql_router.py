from fastapi import APIRouter
from strawberry.fastapi import GraphQLRouter
from app.data.services.graphql_service import schema
from app.documentation.docs import custom_openapi
from pydantic import BaseModel
import os

# Crear el router de GraphQL
graphql_router = APIRouter()

# Definir un modelo Pydantic para el cuerpo de la solicitud
class QueryRequest(BaseModel):
    text: str

# Crear la instancia de GraphQL de Strawberry
graphql_app = GraphQLRouter(schema, graphiql=True)

# Agregar las rutas de GraphQL
graphql_router.include_router(graphql_app, prefix="/query", responses={404: {"description": "Not found"}}, tags=["FastAPI/GraphQL(Strawerry)"])

# Documentación adicional para el endpoint UI de GraphQL/Strawberry
@graphql_router.get("/query", summary="Strawerry/GraphQL UI Endpoint", tags=["FastAPI/GraphQL(Strawerry)"], description="Este endpoint permite interactuar con la UI de Strawerry para GraphQL.")
async def get_graphql_ui():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(graphql_router)
    return custom_openapi(app)