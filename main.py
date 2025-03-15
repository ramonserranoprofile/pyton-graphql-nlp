from fastapi import FastAPI
from app.data.routers.graphql_router import graphql_router
from app.data.routers.nlp_router import nlp_router
# from app.auth.controllers.auth_router import auth_router
# from app.documentation.docs import swagger_ui

app = FastAPI(title="Python GraphQL & NLP API")

# Registrar los routers
app.include_router(graphql_router, prefix="/api")
app.include_router(nlp_router, prefix="/api")
# app.include_router(auth_router, prefix="/api")
# app.include_router(swagger_ui, prefix="/docs")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
