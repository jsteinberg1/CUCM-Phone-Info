import os, time, sys
from datetime import datetime, timedelta
import logging
logger = logging.getLogger('api')

from rq import Queue
from redis import Redis

conn = Redis(os.getenv('REDIS_HOST'), os.getenv('REDIS_PORT'))

from lib.phone_scraper import allDetails

from api.models import phone_data as models
from api.crud import phone_data as crud


def scrape(ip: str, model: str):
    # scrape phone webpage
    try:
        phone_scrape_data = allDetails(ip=ip,model=model)
        logger.debug(f"successfully scraped ip {ip}, attempting to save data to database")
    except NameError:
        logger.error(f"error scraping ip {ip}, unable to find hostname")
        return
    except ConnectionRefusedError as e:
        logger.error(f"error scraping ip {ip}, {e}")
        return
    except Exception as e:
        logger.error('error scraping ip {ip}, at %s', 'render', exc_info=e)
        return

    
    # save to database
    if phone_scrape_data.sn != "":
        
        phone_scrape_data.date_modified = datetime.now()

        try:
            crud.merge_phonescraper_data(phone_scrape_data)
        except Exception as e:
            logger.error(f'error saving ip {ip} to db, at %s', 'render', exc_info=e)
        else:
            logger.debug(f"successfully saved ip {ip} to database")



def rq_scrape_phones(cluster: str = None):
    # scrape phones and write to database

    jobname="phone scraper"
    crud.startjob(jobname=jobname)

    logger.info(f"querying DB for phone info")
    phone_list = crud.get_phone_data_for_phonescraper(cluster_name=cluster)

    # only scrape phones registered in last 24 hours
    phones_reg_in_last_24_hours = []
    for phone in phone_list:
        # only return phones with a last_seen_reg within the last 48 hours
        now = datetime.now()
        if now - timedelta(hours=24) <= phone.last_seen_reg <= now:
            phones_reg_in_last_24_hours.append(phone) # include phones registered in the last 48 hours into list for scraping

    # set RQ queue name
    rq_queue_name = 'phonescraper'
    q = Queue(rq_queue_name, connection=conn)

    # check queue size, if it is more than 25, then it didn't finish from previous run
    if len(q) > 25:
        logger.error(f"RQ {rq_queue_name} length is {len(q)}, skipping run")

    logger.info(f"starting phone scrape")    
    for index, phone in enumerate(phones_reg_in_last_24_hours):
        if phone.ipv4 == '' or phone.ipv4 == None:
            logger.debug(f"skipping {phone.devicename} because no IP is available - {index} out of {len(phones_reg_in_last_24_hours)}")
            continue
        else:
            logger.debug(f"add job for {phone.devicename} {phone.ipv4} - {index} out of {len(phones_reg_in_last_24_hours)}")
        
        # queue scrape to rq
        q.enqueue(scrape,
            kwargs={
                'ip': phone.ipv4,
                'model': phone.Model
            }
        )

    while len(q) > 0:
        logger.debug(f"Redis queue {rq_queue_name} length is {len(q)}")
        time.sleep(30)
    
    crud.endjob(jobname=jobname)

  
if __name__ == "__main__":
    # use for testing
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    os.environ["REDIS_HOST"] = "127.0.0.1"
    os.environ["REDIS_PORT"] = "6379"

    rq_scrape_phones()