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
    """Scrape a single phone IP and write data to database.
    This function is handled by RQ workers

    Arguments:
        ip {str} -- IP address of phone
        model {str} -- Phone model, will be passed to phonescraper function
    """
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
    """Initiate phone scrape update against IP phones

    This function queries IP phone IPS/models from database, and passes the actual scraping to RQ to be handled by workers

    Keyword Arguments:
        cluster {str} -- Can process phone scraper against a single cluster if desired (default: {None})

    """
    
    # Update JobStatus to indicate job started
    jobname="phone scraper"
    crud.startjob(jobname=jobname)

    # Query database for phone IP and model Info
    logger.info(f"querying DB for phone info")
    phone_list = crud.get_phone_data_for_phonescraper(cluster_name=cluster)

    # only scrape phones registered in last 24 hours
    phones_reg_in_last_24_hours = []
    now = datetime.now()
    for phone in phone_list:
        if now - timedelta(hours=24) <= phone.last_seen_reg <= now:
            phones_reg_in_last_24_hours.append(phone) # include phones registered in the last 24 hours into list for scraping

    # set RQ queue name
    rq_queue_name = 'phonescraper'
    q = Queue(rq_queue_name, connection=conn)

    # check queue size, if it is more than 25, then it didn't finish from previous run
    if len(q) > 25:
        logger.error(f"RQ {rq_queue_name} length is {len(q)}, skipping run")

    logger.info(f"starting phone scrape")

    # Loop through all phones and add a scrape job to RQ
    for index, phone in enumerate(phones_reg_in_last_24_hours):
        if phone.ipv4 == '' or phone.ipv4 == None:
            logger.debug(f"skipping {phone.devicename} because no IP is available - {index} out of {len(phones_reg_in_last_24_hours)}")
        else:
            logger.debug(f"add job for {phone.devicename} {phone.ipv4} - {index} out of {len(phones_reg_in_last_24_hours)}")
            q.enqueue(scrape,kwargs={'ip': phone.ipv4,'model': phone.Model}) # Enqueue the scrape job to Redis Queue to be handled by the RQ workers

    # Wait until the Redis Queue length is 0.  Poll queue length every 30 seconds.  This could take hours depending on phone count in clusters
    while len(q) > 0:
        # Phone scrape jobs are still in the RQ
        logger.debug(f"Redis queue {rq_queue_name} length is {len(q)}")
        time.sleep(30)
    
    # Update JobStatus to indicate job finished
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