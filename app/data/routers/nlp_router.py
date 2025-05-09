from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from app.data.services.nlp_service import (
    extract_entities_with_Gemini,
    execute_graphql_query,
    format_response_as_table,
)
from typing import List, Dict
from app.auth.services.auth_service import (
    get_current_active_user,
    check_revoked_token,
)  # Importar la función de autenticación

nlp_router = APIRouter()


# Define Pydantic model to the search query body
class SearchRequest(BaseModel):
    text: str


# Item model (product)
class Item(BaseModel):
    idTieFechaValor: str
    idCliCliente: str
    descGaNombreProducto1: str
    descGaMarcaProducto: str
    descCategoriaProdPrincipal: str
    descGaCodProducto: str
    descGaSkuProducto1: str


# Response Model
class SearchResponse(BaseModel):
    text: str
    items: List[Item]


@nlp_router.post(
    "/search",
    response_model=SearchResponse,
    tags=["FastAPI+NLP(Gemini)"],
    summary="Search products using NLP  Gemini 2.0",
    description="Process the text, extract entities with Gemini 2.0, and finally execute a GraphQL query at '/query' to search for products.",
    dependencies=[Depends(get_current_active_user), Depends(check_revoked_token)],
)
async def search_with_nlp(
    request_body: SearchRequest,
    request: Request,  # Agregar Request como parámetro
):
    """
    Endpoint to search for products using natural language.
    Processes the text, extracts entities, and executes a GraphQL query from the GraphQL endpoint "/query".
    """
    try:
        # Process the text
        entities = (
            extract_entities_with_Gemini(request_body.text) or {}
        )  # Usar empty dictionary if  None
        print("Entidades extraídas:", entities)

        # Build filters to the GraphQL query
        nombre_producto = entities.get("nombre_del_producto", "")
        marca = entities.get("marca", "")
        categoria = entities.get("categoría_principal", "")
        filters = {
            "NombreProducto": nombre_producto.lower(),
            "MarcaProducto": marca.lower(),
            "CategoriaPrincipal": categoria.lower(),
        }
        print("GraphQL filters:", filters)

        # Run GraphQL query with the NLP entities extracted filters
        items = (
            await execute_graphql_query(filters, request) or []
        )  # Use empty List if None
        print("Got Ítems:", len(items))

        # Format response as a table
        table = format_response_as_table(items) if items else "No data found"
        print("Tabla Resultados:\n", table)

        if items and len(items) > 0:
            mensaje = f"{len(items)} products were found that match your query."
            return {"text": mensaje, "items": items}
        else:
            mensaje = "No products were found that match your query."
            return {"text": mensaje, "items": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
