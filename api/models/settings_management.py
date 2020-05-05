from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from api.db.database import Base

class CUCM_Cluster(Base):
    __tablename__ = "cucm_clusters"

    id = Column(Integer, primary_key=True)
    cluster_name = Column(String, unique=True)
    server= Column(String, unique=True)
    version= Column(String)
    username= Column(String)
    pd= Column(String)
    ssl_verification = Column(Boolean)
    ssl_ca_trust_file= Column(String)


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    value = Column(String)


class CUCM_Users(Base):
    __tablename__ = "cucm_users"

    userid = Column(String, primary_key=True)