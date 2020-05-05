from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from pydantic import BaseModel
from api.Auth import Auth

router = APIRouter()

auth = Auth()

class Token(BaseModel):
    access_token: str
    user_name: str
    token_type: str
    expiration: str

@router.post(
  '/get_token',
  response_model=Token,
  response_description="Returns user access token",
  summary="Authenticate API user",
  description="Authenticate an API user and return a token for subsequent requests"
)
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
  a = auth.login(form_data.username, form_data.password)
  if a and a["status"] == "error":
    raise HTTPException(status_code=400, detail={"status": "error", "message": a["message"]})
  return {"access_token": a["token"], "user_name": a["user"], "token_type": "bearer", "expiration": a["expiration"]}


