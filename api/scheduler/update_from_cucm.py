import os

import time, sys
from datetime import datetime
import logging
logger = logging.getLogger('api')

from api.models import phone_data as models
from api.crud import phone_data as crud

from api.scheduler import cisco_mapping


def add_cucm_api_data_2_db(axl_phones_list, serviceability_phones_list, cluster_name):
           
    # Process AXL data into model class
    current_time = datetime.now()
    logger.debug(f"beginning AXL data processing at {current_time}")
    
    # store AXL data in dictionary, it will only be added to DB if the MAC is registered in Serviceability List
    axl_dict = {}
    
    for axl_phone in axl_phones_list:
        try:
            em_profile = axl_phone.currentProfileName._value_1 if axl_phone.currentProfileName._value_1 != None else ""
        except:
            em_profile = ""

        if em_profile == '':
            em_login_timestamp = None
        else:
            em_login_timestamp = datetime.fromtimestamp(int(axl_phone.loginTime))

        try:
            phone_device_pool = axl_phone.devicePoolName._value_1 if axl_phone.devicePoolName._value_1 != None else ""
        except:
            phone_device_pool = ""

        try:
            phone_css = axl_phone.callingSearchSpaceName._value_1 if axl_phone.callingSearchSpaceName._value_1 != None else ""
        except:
            phone_css = ""

        axl_dict[axl_phone.name.upper()] = {
            "devicepool":phone_device_pool,
            "devicecss":phone_css,
            "description":axl_phone.description,
            "em_profile":em_profile,
            "em_time":em_login_timestamp,
        }


    # Process Serviceability data into model class
    logger.debug(f"beginning Serviceability & AXL merge data processing")
    list_models_phone = []

    for phone in serviceability_phones_list:
        phone_devicename = phone.Name.upper()
        phone_reg_timestamp = datetime.fromtimestamp(phone.TimeStamp)
        phone_ip = phone.IPAddress.item[0]['IP']

        phone = models.Phone(
            # serviceability fields
            devicename = phone_devicename,
            firmware = phone.ActiveLoadID,
            ipv4 = phone_ip,
            registration_time = phone_reg_timestamp,
            last_seen_reg = current_time,
            cluster	= cluster_name,
            Protocol = phone.Protocol,
            Model = cisco_mapping.typemodel[str(phone.Model)],

            # AXL fields
            devicepool = axl_dict[phone_devicename]["devicepool"],
            devicecss	= axl_dict[phone_devicename]["devicecss"],
            description	= axl_dict[phone_devicename]["description"],
            em_profile	= axl_dict[phone_devicename]["em_profile"],
            em_time	= axl_dict[phone_devicename]["em_time"],

        )

        list_models_phone.append(phone)

    logger.debug(f"storing {cluster_name} data in database")
    crud.merge_phone_data(list_models_phone)


def update_cucm(axl_ucm, serviceability_ucm, cluster_name):

    jobname=f"{cluster_name} cucm phone sync"

    crud.startjob(jobname=jobname)
    
    logger.info(f"connecting to {cluster_name} AXL")
    try:
        axl_phones = axl_ucm.get_all_phones()
        logger.info(f"retrieved {len(axl_phones)} phones from AXL")
    except:
        logger.error(f"axl error connecting to {cluster_name} - {str(sys.exc_info())}")
        raise (f"axl error connecting to {cluster_name} - {str(sys.exc_info())}")

    if len(axl_phones) == 0:
        raise ValueError(f"No phones were retrieves from AXL, exiting CUCM update function")

    logger.info(f"connecting to {cluster_name} Serviceability API")
    try:
        mac_list = [i.name for i in axl_phones]  # get a list of only MAC addresses from AXL to use in Serviceability query
        serviceability_phones = serviceability_ucm.get_registered_phones(phone_mac_list=mac_list)
        logger.info(f"retrieved {len(serviceability_phones)} phones from Serviceability")
    except:
        logger.error(f"Serviceability error connecting to {cluster_name} - {str(sys.exc_info())}")
        raise (f"Serviceability error connecting to {cluster_name} - {str(sys.exc_info())}")

    logger.info(f"storing {cluster_name} data in database")
    try:
        add_cucm_api_data_2_db(axl_phones, serviceability_phones, cluster_name)
    except:
        logger.error("database error" + str(sys.exc_info()))
    else:
        logger.info("CUCM query & SQL update complete")

    crud.endjob(jobname=jobname)




