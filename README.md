[]: # Title: Python GraphQL NLP Project
[]: # Description: A template for a Python project using GraphQL and NLP.

# Python GraphQL NLP Project

## **Getting Started**

### **1. Set Up the Environment**
```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### **2. Create the Project Structure**
```bash
# Create the main project folder
mkdir python-graphql-nlp && cd python-graphql-nlp

# Create folders for services
mkdir app
cd app
mkdir auth data documentation

# Create subfolders for each service
for service in auth data; do
    mkdir $service/routers $service/models $service/services
done

# Return to the root directory
cd ..

# Create base files
touch app/main.py Dockerfile docker-compose.yml requirements.txt
```

---

## **How to Compile and Run the Project**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Run the Project**
#### **Development Environment**
```bash
uvicorn app.main:app --reload --port 8080
```

#### **Docker Environment**
```bash
docker-compose up --build
```

#### **Production Environment**
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8080
```

---

## **API Endpoints**

### **Data Service**
#### **1. GraphQL Query (POST)**
- **URL**: `http://localhost:8080/api/query`
- **Request Body**:
  ```json
  {
      "query": "query { items { id name description } }",
      "variables": {
          "filters": {
              "key1": "value1",
              "key2": "value2",
              "key3": "value3"
          }
      }
  }
  ```
  e.g. : {
  "query": "query GetProducts($filters: ItemFilter) { items(filters: $filters) { idTieFechaValor idCliCliente descGaNombreProducto1 descGaMarcaProducto descCategoriaProdPrincipal descGaCodProducto descGaSkuProducto1 } }",
  "variables": {
    "filters": {
      "NombreProducto": "martillo percutor",
      "MarcaProducto": "stanley",
      "CategoriaPrincipal": "herramientas"
    }
  }
}

#### **2. GraphQL Query (GET)**
- **URL**: `http://localhost:8080/api/query`
- **Description**: Open the browser and type the URL above to access the GraphQL UI.

#### **3. NLP Search (POST)**
- **URL**: `http://localhost:8080/api/search`
- **Request Body**:
  ```json
  {
      "text": "text to search"
  }

  (e.g. { "text": "busco un martillo marca stanley, ¿tienen en stock?" })
  ```
### **Auth Service**
#### **4. Login (POST)**
- **URL**: `http://localhost:8080/api/login`
- **Request Body**:
  ```json
  {
      "username": "johndoe",
      "password": "secret"
  }
  ```

- **Response**:
  ```json
  {
    "access_token": "<access-token>",
    "token_type": "bearer"
  }

  ```

- **Description**: Description: The access token is used to authenticate requests to protected endpoints. While it is not currently required to be manually provided for these endpoints, it is automatically stored in memory and included when accessing protected resources. However, you can also include the token in the headers, which is a valid approach and recommended for ensuring compatibility with future updates.

#### **5. Logout (POST)**
- **URL**: `http://localhost:8080/api/logout`
- **Response Body**:
  ```json
  {  
    "message": "Sesión cerrada correctamente"
  }
  ```
---

### **Documentation Service**
#### **4. API Documentation**
- **OpenAPI UI**: `http://localhost:8080/api/docs`
- **ReDoc**: `http://localhost:8080/api/redoc`
- **Description**: Open the browser and type the URLs above to access the API documentation.

---

## **Project Structure**
```plaintext
python-graphql-nlp/
├── app/
│   ├── auth/
│   │   ├── routers/
│   │   ├── models/
│   │   └── services/
│   ├── data/
│   │   ├── routers/
│   │   ├── models/
│   │   └── services/
│   ├── documentation/
│── main.py   
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## **Dependencies**
Add the following dependencies to your `requirements.txt` file:
```plaintext
fastapi[standard]
uvicorn[standard]
python-jose[cryptography]
passlib[bcrypt]
python-multipart
pydantic
python-dotenv
strawberry-graphql
openai
gql
requests_toolbelt
aiohttp
```

---

## **Docker Configuration**
### **Dockerfile**
```dockerfile
# Usar una imagen base de Python
FROM python:3.12

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requisitos e instalar dependencias
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que corre la aplicación
EXPOSE 8080

# Ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### **docker-compose.yml**
```yaml
services:
  app:
    build: .
    ports:
      - "8080:8080"
    env_file:
      - .env
```

---

## **Notes**
- Replace placeholders like `key1`, `value1`, etc., with actual values.
- Ensure all environment variables are defined in the `.env` file.
- Use the provided endpoints to interact with the API and access documentation.

```

```json
{
  "username": "johndoe",
  "password": "secret"
}
```

**App Screens Images**
# GraphQL query tool (GET “/query”)
<table>
  <tr>
    <td><img src="./app/static/images/Captura de pantalla 2025-03-17 085528.png" width="195"></td>
    <td><img src="./app/static/images/Captura de pantalla 2025-03-17 094455.png" width="195"></td>    
  </tr>
</table>

# Postman Post Request to /query
<table>
  <tr>
    <td><img src="./app/static/images/Captura de pantalla 2025-03-17 100545.png" width="195"></td>        
  </tr>
</table>

# Postman Post Request to /search
<table>
  <tr>
    <td><img src="./app/static/images/Captura de pantalla 2025-03-17 094621.png" width="195"></td>        
  </tr>
</table>

# OpenAPI 3.0 Documentation "/docs" & "/redoc" Endpoints
<table>
  <tr>
    <td><img src="./app/static/images/Captura de pantalla 2025-03-17 094248.png" width="195"></td>
    <td><img src="./app/static/images/Captura de pantalla 2025-03-17 094342.png" width="195"></td>    
  </tr>
</table>