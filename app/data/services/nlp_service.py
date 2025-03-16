from openai import OpenAI
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio

import os
import json

# Configurar la API key y la URL base de OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("DEEPSEEK_OPENROUTER_API_KEY"),
)


def extract_entities_with_deepseek(text: str) -> dict:
    """
    Envía el texto a DeepSeek (a través de OpenRouter) para extraer entidades.
    """
    # Definir el prompt para DeepSeek
    prompt = f"""
    Extrae del siguiente texto el nombre_del_producto, la marca y la categoría_principal:
    Texto: "{text}".    
    """

    # Enviar la solicitud a OpenRouter usando la librería openai
    response = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://wwww.ramonserranoprofile.com",  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "www.ramonserranoprofile.com",  # Optional. Site title for rankings on openrouter.ai.
        },
        extra_body={},
        model="deepseek/deepseek-r1-zero:free",
        messages=[{"role": "user", "content": prompt}],
    )

    # Extraer el contenido de la respuesta
    content = response.choices[0].message.content
    # Eliminar \boxed y las llaves adicionales de la respuesta
    if content:
        content = content.replace(r'\boxed', '').replace("'", '"').replace("{{", "{").replace("}}", "}").strip()

    else:
        print("La respuesta no contiene contenido válido.")
        return {"nombre_del_producto": "", "marca": "", "categoría_principal": ""}
    # Verificar si el contenido es un JSON válido
    if not content or not content.strip().startswith("{"):
        print("La respuesta no es un JSON válido:", content)
        return {"nombre_del_producto": "", "marca": "", "categoría_principal": ""}

    # Convertir el contenido a un diccionario
    try:
        entities = json.loads(content)
        return entities
    except json.JSONDecodeError as e:
        print("Error al parsear la respuesta:", e)
        return {"nombre_del_producto": "", "marca": "", "categoría_principal": ""}


async def execute_graphql_query(filters):
    transport = AIOHTTPTransport(url="http://127.0.0.1:8080/api/query")
    async with Client(transport=transport) as session:
        query = gql(
            """
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
        )
        result = await session.execute(query, variable_values={"filters": filters})
        return result.get("items", [])


async def format_response_as_table(items: list) -> str:
    """
    Convierte la lista de ítems en una tabla de texto.
    """
    if not items:
        return "No se encontraron resultados."

    # Crear la cabecera de la tabla
    table = "| ID Fecha Valor | ID Cliente | Nombre Producto | Marca | Categoría | Código Producto | SKU |\n"
    table += "|----------------|------------|-----------------|-------|-----------|-----------------|-----|\n"

    # Agregar cada ítem a la tabla
    for item in items:
        table += (
            f"| {item.get('idTieFechaValor', 'N/A')} | {item.get('idCliCliente', 'N/A')} | "
            f"{item.get('descGaNombreProducto1', 'N/A')} | {item.get('descGaMarcaProducto', 'N/A')} | "
            f"{item.get('descCategoriaProdPrincipal', 'N/A')} | {item.get('descGaCodProducto', 'N/A')} | "
            f"{item.get('descGaSkuProducto1', 'N/A')} |\n"
        )

    return table