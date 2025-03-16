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


# Definir el tipo de entrada para los filtros
@strawberry.input
class ItemFilter:
    NombreProducto: Optional[str] = None
    MarcaProducto: Optional[str] = None
    CategoriaPrincipal: Optional[str] = None


# Función para verificar si al menos una palabra coincide
def matches_any_keyword(text: str, keywords: str) -> bool:
    """
    Verifica si al menos una palabra clave está presente en el texto.
    """
    if not keywords:
        return True  # Si no hay palabras clave, no se filtra
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords.split())


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


# Crear el esquema GraphQL
schema = strawberry.Schema(query=Query)
