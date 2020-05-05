import os
import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import atexit

from api.Config import config
from api.db import database
from api.scheduler.Scheduler import scheduler

api = FastAPI()
api.secret_key = os.getenv('SECRET_KEY')

# Configure CORS to allow API requests from NPM
origins = [
    "http://127.0.0.1:8081", # allow npm run serve development
]
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.add_middleware(GZipMiddleware, minimum_size=1000)

logger = logging.getLogger("api")

from .routes import auth, phone_data, settings_management

api.include_router(
  auth.router,
  prefix='/auth',
  tags=["Authentication"]
)

api.include_router(
  phone_data.router,
  prefix='/phonedata',
  tags=["Phone Data Functions"]
)

api.include_router(
  settings_management.router,
  prefix='/settings_management',
  tags=["Settings Management Functions"]
)

api.mount("/home", StaticFiles(directory=os.path.join(config.basedir,"client","dist"), html=True), name="vue-client")

# redirect root to home static path
@api.get("/")
async def redirect():
    response = RedirectResponse(url='/home/index.html')
    return response

# FAST API Startup tasks

@api.on_event('startup')
async def startup_event():
  scheduler.start()
  

# FAST API Shutdown tasks

@api.on_event("shutdown")
async def fastapi_stopped():
  scheduler.shutdown()




