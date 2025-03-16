from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.data.services.nlp_service import extract_entities_with_deepseek, execute_graphql_query, format_response_as_table

nlp_router = APIRouter()


# Definir un modelo Pydantic para el cuerpo de la solicitud
class SearchRequest(BaseModel):
    text: str


@nlp_router.post("/search", response_model=SearchRequest, tags=['FastAPI+NLP(DeepSeek)'], summary="Buscar productos usando NLP con DeepSeek", description="Procesa el texto, extrae entidades con DeepSeek, finalmente ejecuta una consulta GraphQL en '/query' para buscar productos.")
async def search_with_nlp(request: SearchRequest):
    """
    Endpoint para buscar productos usando lenguaje natural.
    Procesa el texto , extrae entidades y ejecuta una consulta GraphQL del GraphQL endpoint "/query".
    """
    try:
        # Procesar el texto
        entities = extract_entities_with_deepseek(request.text)
        print("Entidades extraídas:", entities)
        # Construir los filtros para la consulta GraphQL
        nombre_producto = entities.get("nombre_del_producto", "")
        marca = entities.get("marca", "")
        categoria = entities.get("categoría_principal", "")
        filters = {
            "NombreProducto": nombre_producto.lower(),
            "MarcaProducto": marca.lower(),
            "CategoriaPrincipal": categoria.lower(),
        }
        print("Filtros para la consulta GraphQL:", filters)
        
        # Ejecutar la consulta GraphQL con los filtros extraídos
        items = await execute_graphql_query(filters)
        print("Ítems encontrados:", len(items))
        if items:
            # Formatear la respuesta como una tabla
            table = await format_response_as_table(items)
            # devuelve un json con los items encontrados y un texto en lenguaje natural como que se encontraron len(items) , por otro lado mensaje en caso de que no se encuentren items
            if len(items) > 0:
                mensaje = f"Se encontraron {len(items)} productos que coinciden con su consulta."
                return {"mensaje": mensaje, "Resultados:": items}
            else:
                mensaje = "No se encontraron productos que coincidan con su consulta."
                return {"mensaje": mensaje, "items": len(items)}
        else:
            mensaje = "No se encontraron productos que coincidan con su consulta."
            return {"mensaje": mensaje, "items": len(items)}                    
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
