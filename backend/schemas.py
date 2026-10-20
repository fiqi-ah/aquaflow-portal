from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- User Schemas ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "standard"

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Invoice Schemas ---
class InvoiceCreate(BaseModel):
    customer_name: str
    customer_id: str
    customer_address: str
    bottles_delivered: int

class InvoiceResponse(BaseModel):
    id: int
    customer_name: str
    customer_id: str
    customer_address: str
    bottles_delivered: int
    status: str
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True