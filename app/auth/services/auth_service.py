from fastapi import APIRouter, Depends, HTTPException, status, Request, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Dict, Annotated    
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.datastructures import Headers
import secrets
# Configuración de JWT
# Funcion para crear el Secret Key cadena larga y aleatoria
SECRET_KEY = secrets.token_hex(32)

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


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


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


@auth_router.post("/token", response_model=TokenRequest, tags=["Authentication"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenRequest:
    """
    Obtiene un token de acceso usando OAuth2 con contraseña.
    """
    global current_token
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    current_token = access_token  # Almacenar el token en memoria
    return TokenRequest(access_token=access_token, token_type="bearer")


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


# Lista en memoria de tokens revocados
revoked_tokens = set()

# Endpoint para cerrar sesión
@auth_router.post("/logout", response_model=LogoutResponse, tags=["Authentication"])
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_active_user),
):

    """
    Cierra sesión eliminando el token en memoria y agregándolo a la lista de tokens revocados.
    """
    global current_token

    if token in revoked_tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token ya ha sido revocado",
        )

    # Revocar el token
    revoked_tokens.add(token)

    # Eliminar el token en memoria si coincide con el que se está revocando
    if current_token == token:
        current_token = None

    return LogoutResponse(message="Sesión cerrada correctamente")


# Middleware para verificar si un token está revocado o en token no es el que esta en memoria antes de acceder a recursos protegidos
async def check_revoked_token(token: str = Depends(oauth2_scheme)):
    """
    Verifica si el token está revocado o no es válido.
    """
    global current_token

    # Verificar si el token está en la lista de tokens revocados
    if token in revoked_tokens:
        # Si el token está revocado, eliminarlo de la memoria (si es el token actual)
        if current_token == token:
            current_token = None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado",
        )

    # Verificar si el token no coincide con el token en memoria (opcional)
    if current_token and token != current_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no coincide con el token en memoria",
        )

    return token


# Middleware para agregar el token automáticamente a las solicitudes protegidas
async def add_token_to_request(request: Request, call_next):
    global current_token

    if current_token:
        try:
            # Decodificar el token para verificar si ha expirado
            payload = jwt.decode(current_token, SECRET_KEY, algorithms=[ALGORITHM])
            expire = payload.get("exp")
            if expire and datetime.now(timezone.utc) > datetime.fromtimestamp(expire, tz=timezone.utc):
                # Si el token ha expirado, eliminarlo de la memoria
                current_token = None
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expirado",
                )                    
        except JWTError:
            # Si hay un error al decodificar el token, eliminarlo de la memoria
            current_token = None
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

        # Crear una copia de los encabezados existentes
        headers = dict(request.headers)

        # Agregar el encabezado de autorización
        headers["authorization"] = f"Bearer {current_token}"

        # Crear un nuevo objeto Request con los encabezados modificados
        request._headers = Headers(headers)
        request.scope.update(headers=request.headers.raw)

    response = await call_next(request)
    return response


# Ruta protegida
@auth_router.get(
    "/users/me",
    tags=["Current Active User"],
    response_model=User,
    dependencies=[Depends(get_current_active_user), Depends(check_revoked_token)],
)
async def read_users_me(
    current_user: Annotated[User, [Depends(get_current_active_user), Depends(check_revoked_token)]],
):
    return current_user
