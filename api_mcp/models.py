from pydantic import BaseModel
from typing import Dict, Any

class AuthRequest(BaseModel):
    username: str
    password: str

class ExecuteRequest(BaseModel):
    parametros: Dict[str, Any] = {}
