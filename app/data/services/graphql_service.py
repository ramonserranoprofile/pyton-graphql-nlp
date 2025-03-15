import strawberry
from typing import List, Optional
from app.data.models.graphql_model import ItemType, load_csv_data
import requests
import os

# Cargar los datos desde el CSV
file_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "resources",
    "Data example - Python Coding Challenge - GraphQL.csv",
)
items = load_csv_data(file_path)


# Definir el tipo de entrada para los filtros
@strawberry.input
class ItemFilter:
    NombreProducto: Optional[str] = None
    MarcaProducto: Optional[str] = None
    CategoriaPrincipal: Optional[str] = None


# Resolver de GraphQL
@strawberry.type
class Query:
    @strawberry.field
    def items(self, filters: Optional[ItemFilter] = None) -> List[ItemType]:
        # Si no se proporcionan filtros, devolver todos los productos
        if filters is None:
            return items

        # Filtrar los productos según los argumentos proporcionados
        filtered_items = items

        if filters.NombreProducto:
            filtered_items = [
                item
                for item in filtered_items
                if filters.NombreProducto.lower()
                in item.desc_ga_nombre_producto_1.lower()
            ]

        if filters.MarcaProducto:
            filtered_items = [
                item
                for item in filtered_items
                if filters.MarcaProducto.lower() in item.desc_ga_marca_producto.lower()
            ]

        if filters.CategoriaPrincipal:
            filtered_items = [
                item
                for item in filtered_items
                if filters.CategoriaPrincipal.lower()
                in item.desc_categoria_prod_principal.lower()
            ]

        return filtered_items


def execute_graphql_query(filters: dict) -> dict:
    """
    Ejecuta una consulta GraphQL usando los filtros proporcionados.
    """
    query = """
    query GetProducts($filters: ItemFilter) {
        items(filters: $filters) {
            idTieFechaValor
            idCliCliente
            descGaNombreProducto1
            descGaMarcaProducto
            descCategoriaProdPrincipal
            descGaCodProducto
            descGaSkuProducto1
        }
    }
    """

    variables = {"filters": filters}

    response = requests.post(
        "http://127.0.0.1:8080/api/query", json={"query": query, "variables": variables}
    ).json()

    if "errors" in response:
        raise Exception(f"Error en la consulta GraphQL: {response['errors']}")

    return response.get("data", {})


# Crear el esquema GraphQL
schema = strawberry.Schema(query=Query)
