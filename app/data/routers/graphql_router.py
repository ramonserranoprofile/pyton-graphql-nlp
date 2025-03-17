from fastapi import APIRouter
from strawberry.fastapi import GraphQLRouter
from app.data.services.graphql_service import schema
from app.documentation.docs import custom_openapi
from pydantic import BaseModel
import os

# Create GraphQL router 
graphql_router = APIRouter()

# Define a Pydantic model for the query body
class QueryRequest(BaseModel):
    text: str

# Create GraphQL (Strawberry) instance 
graphql_app = GraphQLRouter(schema, graphiql=True)

# Add GraphQL routes 
graphql_router.include_router(graphql_app, prefix="/query", responses={404: {"description": "Not found"}}, tags=["FastAPI/GraphQL(Strawerry)"])

# Aditional Documentation to the endpoint 
@graphql_router.get("/query", summary="Strawerry/GraphQL UI Endpoint", tags=["FastAPI/GraphQL(Strawerry)"], description="Este endpoint permite hacer consultas GraphQL sobre los datos con la Query Tool de Strawerry.")
async def get_graphql_ui():
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(graphql_router)
    return custom_openapi(app)