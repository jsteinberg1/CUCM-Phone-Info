import os
import io
import time
from pathlib import Path
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Plugin, helpers
from zeep.transports import Transport
from zeep.cache import SqliteCache
from lxml import etree

import logging
logger = logging.getLogger('api')

class MyLoggingPlugin(Plugin):

    def ingress(self, envelope, http_headers, operation):
        logger.debug(f"AXL response: {etree.tostring(envelope, pretty_print=True)}")
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        logger.debug(f"AXL request: {etree.tostring(envelope, pretty_print=True)}")
        return envelope, http_headers

class CUCM_AXL_API(object):

    def __init__(self, server: str, username: str, password: str, cucm_version: str, ssl_verify_cert: bool = True, ssl_ca_trust_file: str = None):
        logger.debug(f"Initializing CUCM AXL object for {server}")

        session = Session()

        # handle SSL verification
        if ssl_verify_cert == True and ssl_ca_trust_file != None:
            session.verify = ssl_ca_trust_file
        else:
            session.verify = ssl_verify_cert
        
        # Handle authentication
        session.auth = HTTPBasicAuth(username, password)

        # Set transport
        transport = Transport(cache=SqliteCache(), session=session, timeout=20)

        try:
            # create Zeep Client object
            wsdl= os.path.join('file://localhost/', Path(os.path.abspath(__file__)).parents[0], 'schema', cucm_version, "AXLAPI.wsdl").replace("\\","/")
            axl_client = Client(wsdl, transport=transport, plugins=[MyLoggingPlugin()])
            
            # WSDL file does not specify server name, set service location
            self.client = axl_client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",f"https://{server}:8443/axl/",)

        except Exception as e:
            logger.error(f"unable to initialize Client object - {e}")
        else:
            logger.debug(f"Inialized CUCM AXL object for {server}")

    
    def authenticateUser(self, username: str, password: str):
        try:
            resp = self.client.doAuthenticateUser(userid= username, password=password)
        except Exception as e:
            logger.error(f'Exception during AXL authenticateUser for username {username} error is {e}')
            return False
        else:
            if 'userAuthenticated' in resp['return']:
                if resp['return']['userAuthenticated'] == 'true':
                    return True
            
            return False

    def get_phones(self, first=1000, skip=0):
        """
        Get phone details
        """
        logger.info(f"AXL get_phones request [ first={first} skip={skip} ]")

        resp = self.client.listPhone(
                {'name': '%'}, returnedTags={
                    'name': '',
                    'devicePoolName': '',
                    'description': '',
                    'callingSearchSpaceName': '',
                    'currentProfileName': '',
                    'loginTime': '',
                }, first=first, skip=skip)

        if resp['return'] == None:
            return []
        else:
            resp = resp['return']['phone']
            return resp
        

    def get_all_phones(self):
        """
        Get all phone details
        """

        batch = 1000  # get 500 phones at a time from AXL
        skip = 0
        max = 100000  # retrieve a max of 40,000 phones
        all_phone_list = []

        while skip <= max:
            try:
                temp_phone_list = self.get_phones(first=batch, skip=skip)
            except Exception as e:
                logger.error(f"get_all_phones error {e}")
                break
            else:
                if len(temp_phone_list) == 0:
                    break

                skip = skip + batch
                all_phone_list = all_phone_list + temp_phone_list
                time.sleep(5)

        return all_phone_list


if __name__ == "__main__":

    from api.Config import config

    for cucm_connection in config.cucm_list:
        if cucm_connection.cluster_name == "admin":
            axl = CUCM_AXL_API(
                server=cucm_connection.server1, 
                username=cucm_connection.username, 
                password=cucm_connection.pd, 
                cucm_version=cucm_connection.version,
                ssl_verify_cert= False
            )
    
    response = axl.get_all_phones()

    #print(response)

    print(len(response))