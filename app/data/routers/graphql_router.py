from fastapi import APIRouter
from strawberry.fastapi import GraphQLRouter
from app.data.services.graphql_service import schema
from typing import List
import os

# Crear el router de GraphQL
graphql_router = APIRouter()

# Crear la instancia de GraphQL de Strawberry
graphql_app = GraphQLRouter(schema)

# Agregar las rutas de GraphQL (HTTP y WebSocket)
graphql_router.include_router(graphql_app, prefix="/query")
