import spacy

# Cargar el modelo de lenguaje en español
nlp = spacy.load("es_core_news_lg")


def process_with_spacy(text: str) -> dict:
    """
    Procesa el texto con spaCy y extrae entidades relevantes.
    """
    doc = nlp(text)

    # Mapeo de etiquetas de spaCy a categorías personalizadas
    entity_mapping = {
        "PER": "MARCA",  # Persona -> Marca
        "LOC": "MODELO",  # Ubicación -> Modelo
        "MISC": "CATEGORIA",  # Misceláneo -> Categoría
    }
    # Extraer entidades (marca, modelo, categoría)
    entities = []
    for ent in doc.ents:
        print(f"Entidad encontrada: {ent.text} -> {ent.label_}")  # Imprimir entidades
        if ent.label_ in entity_mapping:
            entities.append((ent.text, entity_mapping[ent.label_]))

    # Generar un resumen o respuesta contextualizada
    summary = f"En la búsqueda se encontraron los siguientes detalles: {text}. "
    if entities:
        summary += (
            "Se identificaron las siguientes entidades: "
            + ", ".join([f"{ent[0]} ({ent[1]})" for ent in entities])
            + "."
        )

    return {"text": text, "entities": entities, "summary": summary}
