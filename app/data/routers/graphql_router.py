from fastapi import APIRouter, Depends
from strawberry.fastapi import GraphQLRouter
from app.data.services.graphql_service import schema
from app.data.routers.nlp_router import Item
from app.documentation.docs import custom_openapi
from pydantic import BaseModel
import os
from typing import List, Any

# Importar la función de autenticación
from app.auth.services.auth_service import get_current_active_user, check_revoked_token
from typing import Dict

# Create GraphQL router
graphql_router = APIRouter()


# Define a Pydantic model for the query body

class QueryRequest(BaseModel):
    query: str
    variables: Dict[str, str]


class DataResponse(BaseModel):
    items: List[Item]


class QueryResponse(BaseModel):
    data: DataResponse


# Create GraphQL (Strawberry) instance
graphql_app = GraphQLRouter(schema, graphiql=True)

# Add GraphQL routes (protegidas)
graphql_router.include_router(
    graphql_app,
    prefix="/query",
    responses={404: {"description": "Not found"}},
    tags=["FastAPI/GraphQL(Strawberry)"],
    dependencies=[Depends(get_current_active_user), Depends(check_revoked_token)],
)


# Aditional Documentation to the endpoint (protegida)
@graphql_router.get(
    "/query",
    summary="Strawberry/GraphQL UI Endpoint",
    tags=["FastAPI/GraphQL(Strawberry)"],
    description="Este endpoint permite en el navegador hacer consultas GraphQL sobre los datos con la Query Tool GraphiQL integrated development environment.",
    dependencies=[Depends(get_current_active_user), Depends(check_revoked_token)],
)


async def get_graphql_ui():
    """
    Redirige a la interfaz de Strawberry GraphQL (GraphiQL).
    """
    # Redirigir a la interfaz de GraphiQL integrada
    from fastapi.responses import RedirectResponse
    # Forzar un return Ok ó status 200
    return RedirectResponse(url="/query", status_code=200)


@graphql_router.post(
    "/query",
    response_model=QueryResponse,
    summary="Strawberry/GraphQL Endpoint",
    tags=["FastAPI/GraphQL(Strawberry)"],
    description="Este endpoint permite hacer consultas GraphQL sobre los datos con la Query Tool de Strawberry.",
    dependencies=[Depends(get_current_active_user), Depends(check_revoked_token)],
)
async def graphql_query(query_request: QueryRequest):
    # Usar el esquema GraphQL para ejecutar la consulta
    result = schema.execute_sync(query_request.query)
    
    # Retornar la respuesta
    return QueryResponse(data=DataResponse(items=list(result.data.values()) if result.data else []))
