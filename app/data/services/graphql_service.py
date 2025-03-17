import strawberry
from typing import List, Optional
from app.data.models.graphql_model import ItemType, load_csv_data
import os

# Cargar los datos desde el CSV
file_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "resources",
    "Data example - Python Coding Challenge - GraphQL.csv",
)
items = load_csv_data(file_path)


# Define input data type to filters
@strawberry.input
class ItemFilter:
    NombreProducto: Optional[str] = None
    MarcaProducto: Optional[str] = None
    CategoriaPrincipal: Optional[str] = None


# Function to check if at least one word matches
def matches_any_keyword(text: str, keywords: str) -> bool:
    """
    Verifica si al menos una palabra clave está presente en el texto.
    """
    if not keywords:
        return True  # If there are no keywords, no filtering is applied.
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords.split())


# GraphQL Resolver
@strawberry.type
class Query:
    @strawberry.field
    def items(self, filters: Optional[ItemFilter] = None) -> List[ItemType]:
        # If no filters are provided, return all products in the search
        if filters is None:
            return items

        # Filter products based on the provided arguments.
        filtered_items = items

        if filters.NombreProducto:
            filtered_items = [
                item
                for item in filtered_items
                if matches_any_keyword(
                    item.desc_ga_nombre_producto_1, filters.NombreProducto
                )
            ]

        if filters.MarcaProducto:
            filtered_items = [
                item
                for item in filtered_items
                if matches_any_keyword(
                    item.desc_ga_marca_producto, filters.MarcaProducto
                )
            ]

        if filters.CategoriaPrincipal:
            filtered_items = [
                item
                for item in filtered_items
                if matches_any_keyword(
                    item.desc_categoria_prod_principal, filters.CategoriaPrincipal
                )
            ]

        return filtered_items


# Create GraphQL Scheme 
schema = strawberry.Schema(query=Query)
