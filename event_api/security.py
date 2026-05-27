from datetime import datetime, timedelta, UTC
from jose import jwt
from jose import JWTError
from passlib.context import CryptContext

# password hashing config
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# JWT config
SECRET_KEY = "quickcart-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def hash_password(password: str):
    """
    Hash plain password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """
    Verify login password
    """
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):
    """
    Generate JWT token
    """
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str):
    """
    Decode JWT token
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None