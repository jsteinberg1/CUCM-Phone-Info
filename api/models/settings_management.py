from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from api.db.database import Base

class CUCM_Cluster(Base):
    """Model used to store data about CUCM clusters into SQL DB """

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
    """Model used to store application settings in SQL DB """

    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    value = Column(String)


class CUCM_Users(Base):
    """Model used to store users from CUCM that are authorized to login to Phone Info application.
    The process of adding CUCM users to this model is not verified with CUCM.
    However, authentication of said user will fail if the user is not in CUCM
    """

    __tablename__ = "cucm_users"

    userid = Column(String, primary_key=True)