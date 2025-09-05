from pydantic import BaseModel
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    model_config = {"from_attributes": True}

class TokenData(BaseModel):
    username: str | None = None
    
    model_config = {"from_attributes": True}

class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    
    model_config = {"from_attributes": True}

class UserInDB(User):
    hashed_password: str
    
    model_config = {"from_attributes": True}