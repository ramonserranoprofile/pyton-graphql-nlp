from fastapi import FastAPI
from app.data.routers.graphql_router import graphql_router
from app.data.routers.nlp_router import nlp_router
# from app.auth.controllers.auth_router import auth_router
from app.documentation.docs import custom_openapi


app = FastAPI(
    title="Python GraphQL & DeepSeek NLP implementation API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)
@app.get("/", tags=["Root"], include_in_schema=True, response_description="Root Endpoint", response_model=dict, summary="Root Endpoint")
def read_root():
    return {"message": "Hello, world!"}

# Apply documentation API's schemede OpenAPI 3.0 customized
app.openapi = lambda: custom_openapi(app)

# Register the routers
app.include_router(graphql_router, prefix="/api")
app.include_router(nlp_router, prefix="/api")
# app.include_router(auth_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
