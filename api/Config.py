import os
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from typing import List
from pydantic import BaseModel
from OpenSSL import crypto, SSL


logger = logging.getLogger('api')

class ApiConfig:
    """Configuration class used by Phone Info Application"""
    def __init__(self):
        self.basedir = Path(os.path.abspath(__file__)).parents[1]
        logger.info(f"Basedir is set to {self.basedir}")
        self.datafolder = os.path.join(self.basedir, "data")
        self.ca_certs_folder = os.path.join(self.datafolder, "ca_certs")
        self.certs_folder = os.path.join(self.datafolder, "certs")
        self.database_folder = os.path.join(self.datafolder, "database")

        if not os.path.exists(self.datafolder):
            logger.info("data directory doesn't existing, creating..")
            os.mkdir(self.datafolder)
        if not os.path.exists(self.ca_certs_folder):
            logger.info("ca certs directory doesn't existing, creating..")
            os.mkdir(self.ca_certs_folder)
        if not os.path.exists(self.certs_folder):
            logger.info("certs directory doesn't existing, creating..")
            os.mkdir(self.certs_folder)
        if not os.path.exists(self.database_folder):
            logger.info("database directory doesn't existing, creating..")
            os.mkdir(self.database_folder)

        if os.path.exists(os.path.join(self.datafolder, "settings.dat")):
            logger.info("settings.dat file already exists, reading key from file...")
            file = open(os.path.join(self.datafolder, "settings.dat"), 'rb')
            key_data = file.read() # The key will be type bytes
        else:
            logger.info("settings.dat file does not exist, creating new file...")
            key_data = Fernet.generate_key()
            file = open(os.path.join(self.datafolder, "settings.dat"), 'wb')
            file.write(key_data) # The key is type bytes still
        
        # settings.dat key
        self.salt = key_data
        self.key = Fernet(key_data)
        file.close()
        
config = ApiConfig()