from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Dict

# Configuración de JWT
SECRET_KEY = "tu_secret_key_muy_segura"  # Cambia esto por una clave segura
ALGORITHM = "HS256"  # Algoritmo de cifrado
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Tiempo de expiración del token

# Configuración de hasheo de contraseñas
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Configurar el esquema OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Base de datos falsa con contraseñas hasheadas
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("secret"),  # Contraseña hasheada
        "disabled": False,
    }
}

# Almacenamiento en memoria del token
current_token = None


# Modelo de usuario (sin contraseña)
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


# Modelo de usuario en la base de datos (con contraseña hasheada)
class UserInDB(User):
    hashed_password: str


# Función para obtener un usuario de la base de datos
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


# Función para verificar la contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Función para crear un token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Modelo para el cuerpo de la solicitud
class LoginRequest(BaseModel):
    username: str
    password: str


# Crear el router para la autenticación
auth_router = APIRouter()
# Modelo para la respuesta del token
class TokenRequest(BaseModel):
    access_token: str
    token_type: str
    
# Endpoint para generar el token
@auth_router.post("/token", response_model=TokenRequest ,tags=["Authentication"])
async def login(login_request: LoginRequest):
    global current_token
    user_dict = fake_users_db.get(login_request.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    user = UserInDB(**user_dict)
    if not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    current_token = access_token  # Almacenar el token en memoria
    return {"access_token": access_token, "token_type": "bearer"}


# Función para obtener el usuario actual
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username)
    if user is None:
        raise credentials_exception
    return user


# Función para verificar si el usuario está activo
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

# Modelo para la respuesta del logout
class LogoutResponse(BaseModel):
    message: str

# Ruta para cerrar sesión (logout)
@auth_router.post("/logout", response_model=LogoutResponse ,tags=["Authentication"])
async def logout(current_user: User = Depends(get_current_active_user)):
    global current_token
    if current_token:
        current_token = None  # Eliminar el token de la memoria
        return {"message": "Sesión cerrada correctamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay una sesión activa",
        )


# Middleware para agregar el token automáticamente a las solicitudes protegidas
async def add_token_to_request(request: Request, call_next):
    if current_token:
        # Agregar el token a los encabezados de la solicitud
        request.headers.__dict__["_list"].append(
            (b"authorization", f"Bearer {current_token}".encode())
        )
    response = await call_next(request)
    return response


# Ruta protegida
@auth_router.get("/users/me", tags=["Current Active User"], response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
