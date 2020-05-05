from datetime import datetime
from typing import List

from pydantic import BaseModel


class CUCM_Cluster_Base(BaseModel):
    id: int = None
    cluster_name: str
    server: str
    version: str
    username: str
    ssl_verification: bool = True
    ssl_ca_trust_file: str = None


class CUCM_Cluster_Create(CUCM_Cluster_Base):
    pd: str
    

class Settings(BaseModel):
    name: str
    value: str

class CUCM_Users(BaseModel):
    userid: str
