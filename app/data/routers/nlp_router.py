from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.data.services.nlp_service import process_with_spacy
from app.data.services.graphql_service import execute_graphql_query

nlp_router = APIRouter()


# Definir un modelo Pydantic para el cuerpo de la solicitud
class SearchRequest(BaseModel):
    text: str


@nlp_router.post("/search")
def search_with_nlp(request: SearchRequest):
    """
    Endpoint para buscar productos usando lenguaje natural.
    Procesa el texto con spaCy, extrae entidades y ejecuta una consulta GraphQL.
    """
    try:
        # Procesar el texto con spaCy
        processed_data = process_with_spacy(request.text)

        # Extraer entidades relevantes (marca, modelo, categoría)
        filters = {}
        for entity in processed_data.get("entities", []):
            if entity[1] == "MARCA":
                filters["MarcaProducto"] = entity[0]
            elif entity[1] == "MODELO":
                filters["NombreProducto"] = entity[0]
            elif entity[1] == "CATEGORIA":
                filters["CategoriaPrincipal"] = entity[0]

        # Si no se encontraron entidades, devolver un mensaje informativo
        if not filters:
            return {
                "message": "No se encontraron entidades relevantes en el texto.",
                "processed_text": processed_data,
            }

        # Ejecutar la consulta GraphQL con los filtros extraídos
        graphql_response = execute_graphql_query(filters)

        # Devolver la respuesta procesada por spaCy y los resultados de la consulta
        return {"processed_text": processed_data, "graphql_response": graphql_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
