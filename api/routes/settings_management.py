import os, datetime, time, shutil, sqlite3
import copy 
import logging

from fastapi import APIRouter, Depends, Security, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from api.Auth import Auth
from typing import List, Tuple

from api.Config import config

from api.voip.axl import axl_clusters
from api.voip.serviceability import serviceability_clusters
from api.scheduler import Scheduler

from api.models import settings_management as models
from api.crud import settings_management as crud
from api.schemas import settings_management as schemas

logger = logging.getLogger('api')

router = APIRouter()
auth = Auth()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/get_token')

async def is_auth(token: str = Security(oauth2_scheme)):
  return auth.validate(token)


def upload_certificate(cucm_cluster_create: schemas.CUCM_Cluster_Create) -> str:
    """Handles upload of trusted cert used by SSL validation
    Saves cert file in the config.ca_certs_folder

    Arguments:
        cucm_cluster_create {schemas.CUCM_Cluster_Create} -- CUCM cluster model

    Returns:
        str -- name of cert file, will later be stored in SQL DB
    """
    # handle custom certificate
    if cucm_cluster_create.ssl_ca_trust_file != None:
      cert_name = cucm_cluster_create.cluster_name + ".crt"
      file = open(os.path.join(config.ca_certs_folder, cert_name), 'w')
      file.write(cucm_cluster_create.ssl_ca_trust_file)
      file.close()
    else:
      cert_name = None
    
    return cert_name


def read_existing_certificate_file(ssl_ca_trust_file: str):
  """obtain SSL certificate data by reading contents from disk

  Arguments:
      ssl_ca_trust_file {str} -- name of cert file to read

  Returns:
      [type] -- contents of cert file
  """
  if ssl_ca_trust_file != None:
    file = open(os.path.join(config.ca_certs_folder, ssl_ca_trust_file), 'r')
    return file.read()
  else:
    return None


# CUCM Cluster Setting Functions - used by VueJS to display current cluster list
@router.get(
  '/cucm',
   summary="Displays cucm cluster data",
  description="Returns list of cucm clusters",
  response_model=List[schemas.CUCM_Cluster_Base],
  )
def get_cucm_clusters(*, token: str = Security(is_auth)):
    results = crud.get_cucm_clusters()

    list_cucm_cluster_schema_obj = []

    for item in results:

      cert_data = read_existing_certificate_file(item.ssl_ca_trust_file)

      cucm_cluster_schema_obj = schemas.CUCM_Cluster_Base(
        id = item.id,
        cluster_name= item.cluster_name,
        server= item.server,
        version= item.version,
        username= item.username,
        ssl_verification= item.ssl_verification,
        ssl_ca_trust_file = cert_data
      )

      list_cucm_cluster_schema_obj.append(cucm_cluster_schema_obj)

    return list_cucm_cluster_schema_obj

# Delete CUCM cluster -  used by VueJS to delete existing CUCM cluster
@router.delete(
  '/cucm/{id}',
  summary="Deletes specified CUCM Cluster",
  )
def delete_cucm_cluster(id: int, token: str = Security(is_auth)):
    
    try:
        crud.delete_cucm_cluster(id = id)

    except Exception as e:
        logger.error(f"Error {e} generated when attempting to delete cucm cluster {id}")
        raise HTTPException(status_code=400, detail="Delete failed")
    else:
        # reload CUCM API Objects
        axl_clusters.load_clusters()
        serviceability_clusters.load_clusters()
        
        return {"deleted": id}

# Create new CUCM cluster - used by VueJS to create new CUCM cluster
@router.post(
  '/cucm',
  summary="Creates new CUCM cluster entry")
def create_cucm_cluster(cucm_cluster_create: schemas.CUCM_Cluster_Create, token: str = Security(is_auth)):

    log_object = copy.deepcopy(cucm_cluster_create)
    log_object.pd = 'omitted from log'
    logger.info(f"Received request to create new cucm cluster - {log_object}")
    
    # Certificate Management
    cert_name = upload_certificate(cucm_cluster_create)

    # attempt to add new CUCM cluster to application
    try:
        # create new CUCM model
        cucm_cluster = models.CUCM_Cluster(
            cluster_name = cucm_cluster_create.cluster_name,
            server= cucm_cluster_create.server,
            version= cucm_cluster_create.version,
            username= cucm_cluster_create.username,
            ssl_verification = cucm_cluster_create.ssl_verification,
            ssl_ca_trust_file = cert_name,
            pd= cucm_cluster_create.pd,
        )

        # write new CUCM cluster to SQL DB
        crud.merge_cucm_cluster(cucm_cluster)

    except Exception as e:
        logger.error(f"Error {e} generated when attempting to create cucm cluster {cucm_cluster_create.cluster_name}")
        raise HTTPException(status_code=400, detail="Create failed")
    else:
        # reload CUCM API Objects
        axl_clusters.load_clusters()
        
        time.sleep(1)
        
        # validate credentials of new cluster
        axl_object = axl_clusters.get_cluster(cucm_cluster_create.cluster_name)
        auth_result = axl_object.authenticateUser(username=cucm_cluster_create.username, password=cucm_cluster_create.pd)

        logger.info(f"Auth test result for new cluster is {auth_result}")

        if auth_result == False:
          # authentication failed for new cluster, remove entry from database
          crud.delete_cucm_cluster_name(cluster_name=cucm_cluster_create.cluster_name)

          # reload AXL clusters to remove failed cluster from memory
          axl_clusters.load_clusters()

          return {"result": 'failed'}
        else:
          # AXL authentication succeeded for new cluster, reload serviceability object (to load new serviceability object for new cluster)
          serviceability_clusters.load_clusters()

          return {"result": 'success'}

# update CUCM cluster - used by VueJS to modify/edit existing CUCM cluster
@router.put(
  '/cucm/{id}',
  summary="Updates existing CUCM cluster entry")
def update_cucm_cluster(cucm_cluster_create: schemas.CUCM_Cluster_Create, token: str = Security(is_auth)):
    log_object = copy.deepcopy(cucm_cluster_create)
    log_object.pd = 'omitted from log'
    logger.info(f" Received request to update existing cucm cluster - {log_object}")
    
    # Certificate Management
    cert_name = upload_certificate(cucm_cluster_create)

    try:
        cucm_cluster = models.CUCM_Cluster(
            id = cucm_cluster_create.id,
            cluster_name = cucm_cluster_create.cluster_name,
            server= cucm_cluster_create.server,
            version= cucm_cluster_create.version,
            username= cucm_cluster_create.username,
            ssl_verification = cucm_cluster_create.ssl_verification,
            ssl_ca_trust_file = cert_name,
            pd= cucm_cluster_create.pd,
        )
        crud.merge_cucm_cluster(cucm_cluster)

    except Exception as e:
        logger.error(f"Error {e} generated when attempting to edit existing cucm cluster {cucm_cluster_create.cluster_name}")
        raise HTTPException(status_code=400, detail="Edit failed")
    else:
      # reload CUCM API Objects
      axl_clusters.load_clusters()
      serviceability_clusters.load_clusters()

      # validate credentials
      axl_object = axl_clusters.get_cluster(cucm_cluster_create.cluster_name)
      auth_result = axl_object.authenticateUser(username=cucm_cluster_create.username, password=cucm_cluster_create.pd)

      logger.info(f"Auth test result for edited cluster is {auth_result}")

      if auth_result == False:
        return {"result": 'failed'}
      else:
        return {"result": 'success'}


# Accesses and returns all settings data - used by VueJS to display current settings values
@router.get(
  '/settings',
  summary="retrieves all settings value",
  description="Returns all settings value",
  response_model=dict,
  )
def get_all_settings(token: str = Security(is_auth)):
    settings_crud_result = crud.get_all_settings()

    settings_response_dict = {}

    for result in settings_crud_result:
      settings_response_dict[result.name] = result.value

    del settings_response_dict['localadmin'] # remove password before returning settings
   
    return settings_response_dict

# Access specific settings value
@router.get(
  '/settings/{name}',
  summary="retrives Settings value",
  description="Returns settings value",
  response_model=schemas.Settings,
  )
def get_setting(name: str, token: str = Security(is_auth)):
    value = crud.get_setting(name=name)

    return schemas.Settings(name=name, value=value)

# Updates specific setting value
@router.put(
  '/settings',
   summary="updates Settings value",
  description="update settings value",
  response_model=dict,
  )
def put_settings(settings: dict, token: str = Security(is_auth)):
    
    for setting in settings:
      crud.change_setting(name=setting, value=settings[setting])

    Scheduler.reschedule_jobs()

    return get_all_settings()

# Accesses and returns all CUCM authorized users - used by VueJS to display current user list
@router.get(
  '/cucm_users',
  summary="retrives all authorized cucm_users",
  description="Returns all authorized cucm_users",
  response_model=List[str],
  )
def get_all_cucm_users(token: str = Security(is_auth)):
    cucm_users_crud_results = crud.get_all_cucm_users()

    cucm_users_response_list = []

    for result in cucm_users_crud_results:
      cucm_users_response_list.append(result.userid)
    
    return cucm_users_response_list

# adds new user to CUCM authorized user list - used by VueJS to add new user
@router.post(
  '/cucm_users',
  summary="Adds new user to Authorized CUCM User model",
  description="Adds new user to Authorized CUCM User model",
  )
def post_cucm_users(cucm_user: schemas.CUCM_Users, token: str = Security(is_auth)):
  logger.info(f"Post to cucm_users received with value userid: {cucm_user.userid}")

  if len(cucm_user.userid) > 2:
    crud.merge_cucm_user(userid = cucm_user.userid)
    
    return "processed, poll users for verification"

# removes existing user from CUCM authorized user list - used by VueJS to remove CUCM authorized user
@router.delete(
  '/cucm_users/{userid}',
  summary="Adds new user to Authorized CUCM User model",
  description="Adds new user to Authorized CUCM User model",
  )
def delete_cucm_users(userid: str, token: str = Security(is_auth)):
    if len(userid) > 2:
      crud.delete_cucm_user(userid = userid)
    
    return "processed, poll users for verification"

class UpdatePWRequest(BaseModel):
  current: str
  new: str

# Updates 'localadmin' password - used by VueJS to change password
@router.put(
  '/updatepw',
   summary="updates localadmin password value",
  description="update localadmin password value",
  response_model=dict,
  )
def put_updatepw(update_pw_request: UpdatePWRequest, token: str = Security(is_auth)):
    
    result = crud.updatepw(old_password=update_pw_request.current, new_password=update_pw_request.new)
    
    return {'result': result}