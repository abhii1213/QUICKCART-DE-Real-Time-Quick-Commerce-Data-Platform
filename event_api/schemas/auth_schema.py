from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    """
    Customer signup payload
    """
    name: str
    email: EmailStr
    phone: str
    password: str
    city: str
    area: str


class LoginRequest(BaseModel):
    """
    Customer login payload
    """
    email: EmailStr
    password: str