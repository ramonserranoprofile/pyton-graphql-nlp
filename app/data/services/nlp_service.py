from openai import OpenAI
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Set up the API key and base URL for OpenRouter.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("DEEPSEEK_OPENROUTER_API_KEY"),
)


def extract_entities_with_Gemini(text: str) -> dict:
    """
    Envía el texto a Gemini (a través de OpenRouter) para extraer entidades.
    """
    # Define the prompt for the selected NLP.
    prompt = f"""
    Extrae del siguiente texto el nombre_del_producto, la marca y la categoría_principal:
    Texto: "{text}".  Ofrece al respuesta en formato json válido sin hacer embrace en backSticks ni en llaves adicionales, solo el json y no asignes valores como None ó null ó palabras reservadas para la programación a nombre_del_producto, marca y categoría_principal, cuando no tenga valor, usa vacio asi "".
    """

    # Send the request to OpenRouter using the openai library.
    response = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://wwww.ramonserranoprofile.com",  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "www.ramonserranoprofile.com",  # Optional. Site title for rankings on openrouter.ai.
        },
        extra_body={},
        model="google/gemini-2.5-pro-exp-03-25:free",
        response_format={"type": "json_object"},
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


async def execute_graphql_query(filters: Dict) -> Optional[List]:
    """
    Ejecuta una consulta GraphQL con los filtros proporcionados.
    """
    # endpoint GraphQL
    url = "http://127.0.0.1:8080/api/query"

    # Auth Token 
    token = "token_here"

    # Configurate transport with auth token
    transport = AIOHTTPTransport(
        url=url,
        #headers={"Authorization": f"Bearer {token}"},  # Incluir el token en los headers
    )

    # Create client GraphQL
    async with Client(transport=transport) as session:
        # Define GraphQL query
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

        # Run query with data filters
        try:
            result = await session.execute(query, variable_values={"filters": filters})
            return result.get("items", [])
        except Exception as e:
            if "401" in str(e):
                raise Exception(
                    "Error de autenticación: Credenciales inválidas o faltantes."
                )
            else:
                raise Exception(f"Error al ejecutar la consulta GraphQL: {e}")


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
