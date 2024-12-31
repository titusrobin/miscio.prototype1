#backend/app/models/admin.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class AdminBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True

class AdminCreate(AdminBase): #adding password field 
    password: str

class Admin(AdminBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True