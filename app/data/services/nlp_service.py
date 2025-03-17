from openai import OpenAI
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio

import os
import json

# Set up the API key and base URL for OpenRouter.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("DEEPSEEK_OPENROUTER_API_KEY"),
)


def extract_entities_with_deepseek(text: str) -> dict:
    """
    Envía el texto a DeepSeek (a través de OpenRouter) para extraer entidades.
    """
    # Define the prompt for the selected NLP.
    prompt = f"""
    Extrae del siguiente texto el nombre_del_producto, la marca y la categoría_principal:
    Texto: "{text}".  Ofrece al respuesta en formato json válido sin hacer embrace en backSticks ni en llaves adicionales, solo el json.
    """

    # Send the request to OpenRouter using the openai library.
    response = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://wwww.ramonserranoprofile.com",  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "www.ramonserranoprofile.com",  # Optional. Site title for rankings on openrouter.ai.
        },
        extra_body={},
        model="google/gemini-2.0-flash-lite-preview-02-05:free",
        response_format= {"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract the content from the response.
    content = response.choices[0].message.content
    # Remove \boxed and any additional braces from the response.
    if content:
        content = content.replace(r'\boxed', '').replace("'", '"').replace("{{", "{").replace("}}", "}").strip()
        # content = content.replace(r'json', '').split("```")[0].strip()
        # If the response is a valid JSON but enclosed in [] or {}, remove them.
        content = content.replace("[", "").replace("]", "").strip()
        if content.startswith("{"):
            return json.loads(content)
    else:
        print("La respuesta no contiene contenido válido.")
        return {"nombre_del_producto": "", "marca": "", "categoría_principal": ""}
    # Check if the content is a valid JSON.
    if not content or not content.strip().startswith("{"):
        print("La respuesta no es un JSON válido:", content)
        return {"nombre_del_producto": "", "marca": "", "categoría_principal": ""}

    # Convert the content to dict
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


def format_response_as_table(items: list) -> str:
    """
    Convierte la lista de ítems en una tabla de texto.
    """
    if not items:
        return "No se encontraron resultados."

    # Create the table header.
    table = "| ID Fecha Valor | ID Cliente | Nombre Producto | Marca | Categoría | Código Producto | SKU |\n"
    table += "|----------------|------------|-----------------|-------|-----------|-----------------|-----|\n"

    # Add each item to the table.
    for item in items:
        table += (
            f"| {item.get('idTieFechaValor', 'N/A')} | {item.get('idCliCliente', 'N/A')} | "
            f"{item.get('descGaNombreProducto1', 'N/A')} | {item.get('descGaMarcaProducto', 'N/A')} | "
            f"{item.get('descCategoriaProdPrincipal', 'N/A')} | {item.get('descGaCodProducto', 'N/A')} | "
            f"{item.get('descGaSkuProducto1', 'N/A')} |\n"
        )

    return table
