from pydantic import BaseModel

class APIResult(BaseModel):
    success: bool = False
    result: str = None