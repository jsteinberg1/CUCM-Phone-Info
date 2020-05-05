import os
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from typing import List
from pydantic import BaseModel


logger = logging.getLogger('api')

class ApiConfig:
    def __init__(self):
        self.basedir = Path(os.path.abspath(__file__)).parents[1]
        logger.info(f"Basedir is set to {self.basedir}")
        self.datafolder = os.path.join(self.basedir, "data")
        self.ca_certs_folder = os.path.join(self.datafolder, "ca_certs")
        self.certs_folder = os.path.join(self.datafolder, "certs")
        self.database_folder = os.path.join(self.datafolder, "database")

        if not os.path.exists(self.datafolder):
            os.mkdir(self.datafolder)
        if not os.path.exists(self.ca_certs_folder):
            os.mkdir(self.ca_certs_folder)
        if not os.path.exists(self.certs_folder):
            os.mkdir(self.certs_folder)
        if not os.path.exists(self.database_folder):
            os.mkdir(self.database_folder)

        if not os.path.exists(os.path.join(self.datafolder, "settings.dat")):
            key = Fernet.generate_key()
            file = open(os.path.join(self.datafolder, "settings.dat"), 'wb')
            file.write(key) # The key is type bytes still
            file.close()

        
        # settings.dat key
        file = open(os.path.join(self.datafolder, "settings.dat"), 'rb')
        key = file.read() # The key will be type bytes
        self.salt = file.read()
        self.key = Fernet(key)
        file.close()


config = ApiConfig()