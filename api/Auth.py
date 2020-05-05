import os, hashlib
import jwt
import logging
from datetime import datetime, timedelta
from fastapi import HTTPException

from api.Config import config

from api.crud import settings_management

logger = logging.getLogger('api')

class Auth:
  def __init__(self):
    self.SECRET_KEY = os.getenv('SECRET_KEY')
    self.ALGORITHM = "HS256"
    self.ACCESS_TOKEN_EXPIRE_MINUTES = 120


  def authenticate_user(self, username, password, cluster=None):    # authenticate user against CUCM API
    import requests
    
    if username == "localadmin":
      # authenticate to localadmin account
      current_hashed_pw = settings_management.get_setting(name='localadmin')

      supplied_hashed_pw = hashlib.sha512((password + str(config.salt)).encode()).hexdigest()

      if supplied_hashed_pw == current_hashed_pw:
        return True
      else:
        return False
    else:
      # authenticate against CUCM


      authorized_cucm_users = settings_management.get_all_cucm_users()  # get authorized users from DB

      if username in [user_object.userid for user_object in authorized_cucm_users]:
        # user is an authorized CUCM user, authenticate user against CUCM UDS interface for Cluster #1

        cucm_clusters = settings_management.get_cucm_clusters()

        if len(cucm_clusters) > 0:
          logger.info(f"SSL verification status {cucm_clusters[0].ssl_verification}")

          url = "https://" + cucm_clusters[0].server + ":8443/cucm-uds/user/" + username
          session = requests.Session()

          if cucm_clusters[0].ssl_verification == True and cucm_clusters[0].ssl_ca_trust_file != None:
            session.verify = os.path.join(config.ca_certs_folder,cucm_clusters[0].ssl_ca_trust_file)

          if cucm_clusters[0].ssl_verification == False or cucm_clusters[0].ssl_verification == '0':
            session.verify = False

          session.auth = (username, password)
          try:
            response = session.get(url)
          except Exception as e:
            logger.error(f"Auth failure {e}")
          if response.status_code == 200:
              return True

      else:
        return False

    return False

  def login(self, username, password):
    result = self.authenticate_user(username, password)
    if result == True:

        expiration = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

        token = jwt.encode({
            'sub': username,
            'iat': datetime.utcnow(),
            'exp': expiration
        },
        self.SECRET_KEY)

        return {"status": "success", "user": username, "token": token.decode('utf-8'), "expiration": str(expiration)}
    else:
        return {"status": "error", "message": "username/password incorrect"}


  def validate(self, token):
    try:
      data = jwt.decode(token, self.SECRET_KEY)
    except Exception as e:
      if "expired" in str(e):
        raise HTTPException(status_code=401, detail={"status": "error", "message": "Token expired"})
      else:
        raise HTTPException(status_code=400, detail={"status": "error", "message": "Exception: " + str(e)})
    return data