
import logging
logger = logging.getLogger('api')
from apscheduler.schedulers.background import BackgroundScheduler

from api.Config import config
from api.voip.axl import axl_clusters 
from api.voip.serviceability import serviceability_clusters
from api.crud import settings_management

# background task functions

def scheduler_phone_sync(manual=False):
  scheduler.pause()
  
  if manual:
    trigger_method = "manual"
  else:
    trigger_method = "scheduled"

  logger.info(f'APscheduler {trigger_method} cucm phone sync triggered')

  from api.scheduler import update_from_cucm
  
  for cluster in axl_clusters.clusters:
    update_from_cucm.update_cucm(
      axl_ucm= axl_clusters.get_cluster(cluster_name=cluster), 
      serviceability_ucm= serviceability_clusters.get_cluster(cluster_name=cluster), 
      cluster_name=cluster
    )

  scheduler.resume()

def scheduler_phonescrape_sync(manual=False):
  scheduler.pause()

  if manual:
    trigger_method = "manual"
    
  else:
    trigger_method = "scheduled"

  logger.info('APscheduler {trigger_method} phonescrape update triggered')

  from api.scheduler.update_from_phonescraper import rq_scrape_phones

  rq_scrape_phones()

  scheduler.resume()

# scheduler init
scheduler = BackgroundScheduler()

# get times from settings
settings = settings_management.get_all_settings()

settings_dict = {}
for setting in settings:
  settings_dict[setting.name] = setting.value

scheduler_phone_sync_job = scheduler.add_job(scheduler_phone_sync, 'cron', hour='*', minute=settings_dict['cucm_update_minute'])
scheduler_phonescrape_sync_job = scheduler.add_job(scheduler_phonescrape_sync, 'cron', hour=settings_dict['phonescrape_update_time'].split(':')[0], minute=settings_dict['phonescrape_update_time'].split(':')[1])
  

def reschedule_jobs():
  logger.info("rescheduling jobs..")
  # get times from settings
  settings = settings_management.get_all_settings()

  settings_dict = {}

  for setting in settings:
    settings_dict[setting.name] = setting.value

  scheduler_phone_sync_job.reschedule(trigger='cron', hour='*', minute=settings_dict['cucm_update_minute'])
  scheduler_phonescrape_sync_job.reschedule(trigger='cron', hour=settings_dict['phonescrape_update_time'].split(':')[0], minute=settings_dict['phonescrape_update_time'].split(':')[1])

