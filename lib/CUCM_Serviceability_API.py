import os
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.exceptions import Fault
from zeep.transports import Transport
from zeep.cache import SqliteCache
import time

import logging
logger = logging.getLogger('api')

from api.Config import config

# creates serviceability client for querying serviceability API

def splitlist(l,n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


class CUCM_Serviceability_API(object):


    def __init__(self, server: str, username: str, password: str, ssl_verify_cert: bool = True, ssl_ca_trust_file: str = None):
        self.username = username
        self.password = password
        self.wsdl = f'https://{server}:8443/realtimeservice2/services/RISService70?wsdl'
        self.server = server

        logger.debug(f"Inializing CUCM serviceability object for {self.server}")

        # Build Client Object for RisPort70 Service
        session = Session()
        if ssl_verify_cert == True and ssl_ca_trust_file != None:
            session.verify = ssl_ca_trust_file
        else:
            session.verify = ssl_verify_cert
        session.auth = HTTPBasicAuth(username, password)

        transport = Transport(cache=SqliteCache(), session=session, timeout=20)

        try:
            self.client = Client(self.wsdl, transport=transport)

            # The WSDL has the IP embedded which breaks certificate validation, change this to FQDN
            self.client.wsdl.services['RISService70'].ports['RisPort70'].binding_options['address'] = f'https://{self.server}:8443/realtimeservice2/services/RISService70'
        except:
            logger.error("unable to initialize Client object")
        else:
            logger.debug(f"Inialized CUCM serviceability object for {self.server}")


    def get_registered_phones(self, phone_mac_list, querylimit=1000):
        serviceability_phones_list = []

        # split phones into multiple lists if needed
        if len(phone_mac_list) > querylimit:
            phone_mac_list = list(splitlist(phone_mac_list, querylimit))
        else:
            # embeed the phone list in another list
            phone_mac_list = [phone_mac_list]
        i=0
        for batch_of_phones in phone_mac_list:
            i+=1
            batch_phone_results_list = []

            logger.info(f"Serviceability query batch {i} of {len(phone_mac_list)}")

            # Run SelectCmDeviceExt
            CmSelectionCriteria = {
                'MaxReturnedDevices': '1000',
                'DeviceClass': 'Phone',
                'Model': '255',
                'Status': 'Registered',
                'NodeName': '',
                'SelectBy': 'Name',
                'SelectItems': {
                    'item': batch_of_phones
                },
                'Protocol': 'Any',
                'DownloadStatus': 'Any'
            }

            StateInfo = ''
            try:
                resp = self.client.service.selectCmDeviceExt(
                    CmSelectionCriteria=CmSelectionCriteria,
                    StateInfo=StateInfo)
            except Fault:
                raise

            CmNodes = resp.SelectCmDeviceResult.CmNodes.item
            for CmNode in CmNodes:
                if len(CmNode.CmDevices.item) > 0:
                    # If the node has returned CmDevices, save to the snapshot to
                    # later compare
                    for item in CmNode.CmDevices.item:
                        # Creates a new list if the key in the dictionary isn't yet
                        # assigned or simply appends to the entry if there is already
                        # a value present

                        if (item.Status == "Registered"):  # only keep data for registered phones
                            batch_phone_results_list.append(item)

            serviceability_phones_list = serviceability_phones_list + batch_phone_results_list
            if(len(phone_mac_list)!=i):
                time.sleep(10)  # delay a little in between querying Serviceability to prevent overloading system

        return serviceability_phones_list
