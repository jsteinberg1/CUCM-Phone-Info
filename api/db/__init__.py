import os, hashlib

from api.Config import config
from api.db.database import engine, Base, database_file_name

# create SQL lite file if it doesn't exist
if not os.path.exists(database_file_name):
    from api.models.phone_data import Phone, PhoneScraper, JobStatus
    from api.models.settings_management import CUCM_Cluster
    Base.metadata.create_all(bind=engine)

    # populate settings table with initial values
    from api.crud import settings_management as crud

    crud.change_setting(name = 'cucm_update_minute', value='50')
    crud.change_setting(name = 'phonescrape_update_time', value='01:30')

    default_password_hash = hashlib.sha512(('setup' + str(config.salt)).encode()).hexdigest()
    crud.change_setting(name = 'localadmin', value=default_password_hash)
