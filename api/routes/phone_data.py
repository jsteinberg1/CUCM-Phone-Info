import os, datetime, time, shutil, sqlite3
import logging

from fastapi import APIRouter, Depends, Security, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from api.Auth import Auth
from typing import List, Tuple

from api.Config import config
from api.Main import scheduler
from api.models import phone_data as models
from api.schemas import phone_data as schemas
from api.crud import phone_data as crud

logger = logging.getLogger('api')

router = APIRouter()
auth = Auth()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/get_token')

async def is_auth(token: str = Security(oauth2_scheme)):
  return auth.validate(token)


class RQ_Queue_Status(BaseModel):
  current_size: int
  started_count: int

# Job Status Poll
@router.get(
  '/jobstatus',
  summary="Displays job status and apscheduler state",
  description="Returns current job status state"
)
def get_state(*, token: str = Security(is_auth)):
  jobstatus = crud.get_all_jobstatus()

  # get redis queue stats
  try:
    from redis import Redis
    from rq import Queue

    conn = Redis(os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT')) 

    q = Queue('phonescraper', connection=conn)
    
    RQ_Status = RQ_Queue_Status(
          current_size= len(q),
          started_count= len(q.started_job_registry)
        )
  except:
    logger.error("Unable to connect to redis")
    RQ_Status = RQ_Queue_Status(current_size = -1, started_count = -1)

  return {
    "Job_Status": jobstatus,
    "RQ_Status": RQ_Status
  }


# Trigger manual phone data update now
@router.get(
  '/poll_cucm_now',
  summary="Triggers manual poll of phone data",
  description="Returns true if triggered"
)
async def get_poll_cucm_now(*, token: str = Security(is_auth), background_tasks: BackgroundTasks):
  from api.scheduler.Scheduler import scheduler, scheduler_phone_sync
  if scheduler.state == 1:
    background_tasks.add_task(scheduler_phone_sync,manual=True)
  return {"Result": "phone sync update queued"}

# Trigger manual phone data update now
@router.get(
  '/initiate_phone_scrape_now',
  summary="Triggers manual run of phonescraper",
  description="Returns true if triggered"
)
async def get_initiate_phone_scrape_now(*, token: str = Security(is_auth), background_tasks: BackgroundTasks):
  from api.scheduler.Scheduler import scheduler, scheduler_phonescrape_sync
  if scheduler.state == 1:
    background_tasks.add_task(scheduler_phonescrape_sync,manual=True)
  return {"Result": "phone sync update queued"}



# Phone Data
@router.get(
  '/info',
   summary="Displays phone data",
  description="Returns list of phone data",
  response_model=List[schemas.PhoneInfo],
  )
def get_phone_info(*, token: str = Security(is_auth)):
    results = crud.get_all_phone_data()

    list_phone_schema_obj = []

    for item in results:

      phone_schema_obj = schemas.PhoneInfo(
          dname = item.devicename,
          fw = item.firmware,
          ipv4 = item.ipv4,
          fdate = "" if item.first_seen_reg is None else item.first_seen_reg.strftime("%m/%d/%y %H:%M:%S"),
          ldate = "" if item.last_seen_reg is None else item.last_seen_reg.strftime("%m/%d/%y %H:%M:%S") ,
          regstamp = "" if item.registration_time is None else item.registration_time.strftime("%m/%d/%y %H:%M:%S"),
          cluster = item.cluster,
          prot = item.Protocol,
          model = item.Model.replace("Cisco ",""),

          # AXL Fields
          dpool = item.devicepool,
          dcss = item.devicecss,
          descr = item.description,
          em_profile = item.em_profile,
          em_time =  "" if item.em_time is None else item.em_time.strftime("%m/%d/%y %H:%M:%S"),
      )

      list_phone_schema_obj.append(phone_schema_obj)

    return list_phone_schema_obj

# Phone Data
@router.get(
  '/scraper',
   summary="Displays phone scraper",
  description="Returns list of phone scraper",
  response_model=List[schemas.PhoneScraper],
  )
def get_phone_scraper_info(*, token: str = Security(is_auth)):
    results = crud.get_all_scraper_data()

    list_phone_scraper_schema_obj = []

    for item in results:

      if item.phonescrape == None:
        phone_schema_obj = schemas.PhoneScraper(
          devicename = item.devicename,
          model = item.Model,
          ip_address = item.ipv4
        )
      else:
        phone_schema_obj = schemas.PhoneScraper(
          devicename = item.devicename,
          sn = item.phonescrape.sn,
          firmware = item.phonescrape.firmware,
          dn = item.phonescrape.dn,
          model = item.phonescrape.model,
          kem1 = item.phonescrape.kem1,
          kem2 = item.phonescrape.kem2,
          domain_name = item.phonescrape.domain_name,
          dhcp_server = item.phonescrape.dhcp_server,
          dhcp = item.phonescrape.dhcp,
          ip_address = item.phonescrape.ip_address,
          subnetmask = item.phonescrape.subnetmask,
          gateway = item.phonescrape.gateway,
          dns1 = item.phonescrape.dns1,
          dns2 = item.phonescrape.dns2,
          alt_tftp = item.phonescrape.alt_tftp,
          tftp1 = item.phonescrape.tftp1,
          tftp2 = item.phonescrape.tftp2,
          op_vlan = item.phonescrape.op_vlan,
          admin_vlan = item.phonescrape.admin_vlan,
          cucm1 = item.phonescrape.cucm1,
          cucm2 = item.phonescrape.cucm2,
          cucm3 = item.phonescrape.cucm3,
          cucm4 = item.phonescrape.cucm4,
          cucm5 = item.phonescrape.cucm5,
          info_url = item.phonescrape.info_url,
          dir_url = item.phonescrape.dir_url,
          msg_url = item.phonescrape.msg_url,
          svc_url = item.phonescrape.svc_url,
          idle_url = item.phonescrape.idle_url,
          info_url_time = item.phonescrape.info_url_time,
          proxy_url = item.phonescrape.proxy_url,
          auth_url = item.phonescrape.auth_url,
          tvs = item.phonescrape.tvs,
          CDP_Neighbor_ID = item.phonescrape.CDP_Neighbor_ID,
          CDP_Neighbor_IP = item.phonescrape.CDP_Neighbor_IP,
          CDP_Neighbor_Port = item.phonescrape.CDP_Neighbor_Port,
          LLDP_Neighbor_ID = item.phonescrape.LLDP_Neighbor_ID,
          LLDP_Neighbor_IP = item.phonescrape.LLDP_Neighbor_IP,
          LLDP_Neighbor_Port = item.phonescrape.LLDP_Neighbor_Port,
          ITL = item.phonescrape.ITL,
          date_modified = "" if item.phonescrape.date_modified is None else item.phonescrape.date_modified.strftime("%m/%d/%y %H:%M:%S"),
        )

      list_phone_scraper_schema_obj.append(phone_schema_obj)

    return list_phone_scraper_schema_obj


class Device_Pool_List(BaseModel):
  device_pool_list: List[str]

@router.get(
    '/device_pool_list',
    response_model=Device_Pool_List,
    summary="Device Pool List",
    description="Returns a list of device pools from phone info table"
    )
async def get_device_pool_list(token: str = Security(is_auth)):
  result = crud.get_device_pool_list()

  device_pool_list = Device_Pool_List(device_pool_list=result)

  return device_pool_list




