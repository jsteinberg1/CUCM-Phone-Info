import sys
from datetime import datetime

import logging
from sqlalchemy.orm import Session, joinedload, contains_eager
from typing import List

from api.db.database import SessionLocal
from api.models import phone_data as models

logger = logging.getLogger('api')

# phone data

def get_all_phone_data(db: Session = SessionLocal()):

    results = db.query(models.Phone).all()

    db.close()
    return results

def merge_phone_data(phone_list: List[models.Phone], db: Session = SessionLocal()):
    for phone in phone_list:
        db.merge(phone)
    
    db.commit()
    db.close()


def get_phone_data_by_cluster(cluster_name: str, db: Session = SessionLocal()):
    result = db.query(models.Phone).filter(models.Phone.cluster == cluster_name).all()
    db.close()
    return result


def get_phone_data_for_phonescraper(cluster_name: str = None, db: Session = SessionLocal()):
    
    query = db.query(models.Phone)

    if cluster_name != None:
        query = query.filter(models.Phone.cluster == cluster_name)
        
    results = query.all()

    db.close()
    
    return results

def get_device_pool_by_devicename(device_name: str, db: Session = SessionLocal()):

    result = db.query(models.Phone.devicepool).filter(models.Phone.devicename==device_name).first()
    db.close()

    return result

def get_device_pool_list(db: Session = SessionLocal()):

    result = db.query(models.Phone.devicepool).distinct().all()
    db.close()

    device_pool_list = [item[0] for item in result]

    return device_pool_list

# phone scraper

def get_all_scraper_data(db: Session = SessionLocal()):

    results = db.query(models.Phone).options(
        joinedload(models.Phone.phonescrape),
    ).all()

    db.close()

    return results


def get_phonescraper_by_devicename(hostname: str, db: Session = SessionLocal()):
    result = db.query(models.PhoneScraper).filter(models.PhoneScraper.hostname == hostname).first()
    db.close()
    return result


def merge_phonescraper_data(phonescraper_data: models.PhoneScraper, db: Session = SessionLocal()):
    db.merge(phonescraper_data)
    db.commit()
    db.close()

# Job Status

def startjob(jobname: str, db: Session = SessionLocal()):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Starting {jobname} at {current_time}")
    job_update = models.JobStatus(jobname=jobname, laststarttime=current_time, result="running job..")
    db.merge(job_update)
    db.commit()
    db.close()


def endjob(jobname: str, db: Session = SessionLocal()):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Finished {jobname} at {current_time}")
    job_update = models.JobStatus(jobname=jobname, result=f"Finished at {current_time}")
    db.merge(job_update)
    db.commit()
    db.close()

def get_all_jobstatus(db: Session = SessionLocal()):
    result = db.query(models.JobStatus).all()
    db.close()
    return result