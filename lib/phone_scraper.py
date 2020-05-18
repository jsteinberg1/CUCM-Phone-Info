import os
import subprocess
import platform
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

import logging
logger = logging.getLogger('api')

from api.models.phone_data import PhoneScraper


def connect_to_phone(url: str):
    """Connect to phone URLS and collect response

    Arguments:
        url {str} -- URL to phone webpage

    Raises:
        ConnectionRefusedError: Unable to connect to phone URL

    Returns:
        response_text -- BS4 parsed requests response
    """
    
    headers = {}
    requests_time = 3
    
    logger.debug(f"Querying URL {url}")

    try:
        response = requests.request("GET", url, headers=headers, timeout=requests_time)
    except requests.exceptions.ConnectTimeout:
        raise ConnectionRefusedError(f"request timed out")
    except requests.exceptions.RequestException as e:
        raise ConnectionRefusedError(f"unable to connect {e} - {url}")

    # parse requests response with Beautiful Soup
    response_soup = BeautifulSoup(response.text, features="lxml")
    response_text = response_soup.get_text('_')
    
    return response_text


def regex_search_and_assign_if_match(attribute: str, regex_pattern: str, raw_source_text: str, phonescraper_object: PhoneScraper, regex_group: int = 2) -> PhoneScraper:
    # use regex to search for regex_pattern in raw_source_text
    regex_search_result = re.search(regex_pattern, raw_source_text)
    
    if regex_search_result:
        try:
            regex_result = regex_search_result.group(regex_group).strip() # the value we want is in the second regex group match
            setattr(phonescraper_object, attribute, regex_result)  # assign value to attribute on phonescrape object
        except Exception as e:
            logger.error(f"Regex search failure for {attribute} using regex {regex_pattern} failed due to {e}")

    # return object
    return phonescraper_object


def parse_standard_models(model: str, config_text: str, device_text: str, status_text: str, network_text: str) -> PhoneScraper:
    """Parse phone responses using BeautifulSoup

    Arguments:
        model {str} -- Cisco model number
        config_text {str} -- BS4 parsed requests response from config URL
        device_text {str} -- BS4 parsed requests response from device URL
        status_text {str} -- BS4 parsed requests response from status URL
        network_text {str} -- BS4 parsed requests response from network URL

    Raises:
        NameError: [description]

    Returns:
        PhoneScraper -- PhoneScraper model object
    """
    
    # ***** Config Parser *****
    if config_text != None:

        # Hostname parser & instantiate phonescraper object
        res = re.search(r'(Host Name_\n_\n_|Host name_|Host Name_)([^(_| )]*)', config_text)
        if res:
            temp_hostname = ""
            temp_hostname =  res.group(2).strip()
            phone_scrape_data = PhoneScraper(devicename=temp_hostname)
        else:
            raise NameError("Unable to locate hostname/devicename")

        phone_scrape_data = regex_search_and_assign_if_match('domain_name', '(Domain Name_\n_\n_|Domain name_|Domain Name_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('dhcp_server', '(DHCP Server_\n_\n_|DHCP server_|DHCP Server_)([^(_| )]*)', config_text, phone_scrape_data)             
        phone_scrape_data = regex_search_and_assign_if_match('dhcp', '(DHCP Enabled_\n_\n_|DHCP Enabled_|DHCP_)([^(_| )]*)', config_text, phone_scrape_data)            
        phone_scrape_data = regex_search_and_assign_if_match('ip_address', '(IP Address_\n_\n_|IP address_|IP Address_)([^(_| )]*)', config_text, phone_scrape_data)            
        phone_scrape_data = regex_search_and_assign_if_match('subnetmask', '(Subnet Mask_\n_\n_|Subnet mask_|Subnet Mask_)([^(_| )]*)', config_text, phone_scrape_data)              
        phone_scrape_data = regex_search_and_assign_if_match('gateway', '(Default Router 1_\n_\n_|Default router_|Default Router 1_|Default Router_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('dns1', '(DNS Server 1_\n_\n_|DNS server 1_|DNS Server 1_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('dns2', '(DNS Server 2_\n_\n_|DNS server 2_|DNS Server 2_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('alt_tftp', '(Alternate TFTP_\n_\n_|Alternate TFTP_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('tftp1', '(TFTP Server 1_\n_\n_|TFTP server 1_|TFTP Server 1_|TFTP Server 1)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('tftp2', '(TFTP Server 2_\n_\n_|TFTP server 2_|TFTP Server 2_|TFTP Server 2)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('op_vlan', '(Operational VLAN Id_\n_\n_|Operational VLAN ID_|Operational VLAN Id_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('admin_vlan', '(Admin. VLAN Id_\n_\n_|Admin VLAN ID_|Admin VLAN Id_)([^(_| )]*)', config_text, phone_scrape_data)      
        
        # CUCM server parser - some models differ on this
        if model == "8821":
            phone_scrape_data = regex_search_and_assign_if_match('cucm1', '( Server 1_)([^(_| )]*)', config_text, phone_scrape_data)
            phone_scrape_data = regex_search_and_assign_if_match('cucm2', '( Server 2_)([^(_| )]*)', config_text, phone_scrape_data)
            phone_scrape_data = regex_search_and_assign_if_match('cucm3', '( Server 3_|Server 3 SRST_\n_\n_)([^(_| )]*)', config_text, phone_scrape_data) 
            phone_scrape_data = regex_search_and_assign_if_match('cucm4', '( Server 4_|Server 4 SRST_\n_\n_)([^(_| )]*)', config_text, phone_scrape_data)
            phone_scrape_data = regex_search_and_assign_if_match('cucm5', '( Server 5_)([^(_| )]*)', config_text, phone_scrape_data)
        else:
            phone_scrape_data = regex_search_and_assign_if_match('cucm1', '(CUCM server1|CUCM Server1|Unified CM 1|Unified CM1|CallManager 1|Call Manager 1)( SRST| TFTP)?(_\n_\n_|_)?([^(_| )]*)', config_text, phone_scrape_data, 4)         
            phone_scrape_data = regex_search_and_assign_if_match('cucm2', '(CUCM server2|CUCM Server2|Unified CM 2|Unified CM2|CallManager 2|Call Manager 2)( SRST| TFTP)?(_\n_\n_|_)?([^(_| )]*)', config_text, phone_scrape_data, 4)       
            phone_scrape_data = regex_search_and_assign_if_match('cucm3', '(CUCM server3|CUCM Server3|Unified CM 3|Unified CM3|CallManager 3|Call Manager 3)( SRST| TFTP)?(_\n_\n_|_)?([^(_| )]*)', config_text, phone_scrape_data, 4)          
            phone_scrape_data = regex_search_and_assign_if_match('cucm4', '(CUCM server4|CUCM Server4|Unified CM 4|Unified CM4|CallManager 4|Call Manager 4)( SRST| TFTP)?(_\n_\n_|_)?([^(_| )]*)', config_text, phone_scrape_data, 4)          
            phone_scrape_data = regex_search_and_assign_if_match('cucm5', '(CUCM server5|CUCM Server5|Unified CM 5|Unified CM5|CallManager 5|Call Manager 5)( SRST| TFTP)?(_\n_\n_|_)?([^(_| )]*)', config_text, phone_scrape_data, 4)
            
        # URL parser
        phone_scrape_data = regex_search_and_assign_if_match('info_url', '(Information URL_)([^(_| )]*)', config_text, phone_scrape_data)      
        phone_scrape_data = regex_search_and_assign_if_match('dir_url', '(Directories URL_)([^(_| )]*)', config_text, phone_scrape_data)               
        phone_scrape_data = regex_search_and_assign_if_match('msg_url', '(Messages URL_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('svc_url', '(Services URL_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('idle_url', '(Idle URL_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('info_url_time', '(Idle URL time_)([^(_| )]*)', config_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('proxy_url', '(Proxy Server URL_|Proxy server URL)([^(_| )]*)', config_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('auth_url', '(Authentication URL_)([^(_| )]*)', config_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('tvs', '(TVS_)([^(_| )]*)', config_text, phone_scrape_data)

    # ***** Device Parser *****
    if device_text != None:
        phone_scrape_data = regex_search_and_assign_if_match('sn', '(Serial Number_\n_\n_|Serial number_|Serial Number_)([^(_| |_\n)]*)', device_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('firmware', '(Version__\n_\n_|Version_)([^(_| )]*)', device_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dn', '(Phone DN_\n_\n_|Phone DN_)([^(_| )]*)', device_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('model', '(Model Number_\n_\n_|Model number_|Model Number_)([^(_| )]*)', device_text, phone_scrape_data)
        if hasattr(phone_scrape_data, 'model'):
            if 'CP' in phone_scrape_data.model: # Normalize model info
                phone_scrape_data.model = phone_scrape_data.model.replace('CP-', '')
        
        phone_scrape_data = regex_search_and_assign_if_match('kem1', '(Key expansion module 1_|Key Expansion Module 1_)([^(_| )]*)', device_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('kem2', '(Key expansion module 2_|Key Expansion Module 2_)([^(_| )]*)', device_text, phone_scrape_data)      

    # ***** Network Parser *****
    if network_text != None:
        phone_scrape_data = regex_search_and_assign_if_match('CDP_Neighbor_ID', '(Neighbor Device ID_\n_\n_|CDP Neighbor device ID_|CDP Neighbor Device ID_)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('CDP_Neighbor_IP', '(Neighbor IP Address_\n_\n_|CDP Neighbor IP address_|CDP Neighbor IP Address_)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('CDP_Neighbor_Port', '(Neighbor Port_\n_\n_|CDP Neighbor Port_|CDP Neighbor port_)([^_]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('LLDP_Neighbor_ID', '(LLDP Neighbor Device ID_|LLDP Neighbor device ID_)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('LLDP_Neighbor_IP', '(LLDP Neighbor IP Address_|LLDP Neighbor IP address_)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('LLDP_Neighbor_Port', '(LLDP Neighbor Port_|LLDP Neighbor port_)([^(_| )]*)', network_text, phone_scrape_data)       
    
    # Status parser (includes ITL)
    if status_text != None:
        
        errors = []
        if phone_scrape_data.model != "":
            if phone_scrape_data.model in ['7941', '7961', '7962', '7942']:
                statuses = (re.findall(r'(\d{1,2}:..:..[ap]) ([^(_)]*)', status_text))
                for status in statuses[-10:]:
                    errors.append(status[0] + ' ' + status[1])
                    for x in ['trust', 'itl']:
                        if x in status[1].lower():
                            phone_scrape_data.ITL =  status[1]
            elif phone_scrape_data.model == '8831':
                statuses = re.findall(r'[.{1,2}:..:..[ap] ..\/..\/..](\n)([^(_)]*)', status_text)
                for status in statuses[-10:]:
                    errors.append(status[0] + ' ' + status[1])
                    for x in ['trust', 'itl']:
                        if x in status[1].lower():
                            phone_scrape_data.ITL =  status[1]
            else:
                statuses = re.findall(r'(..:..:...m ..\/..\/...)(\n)([^(_)]*)', status_text)
                for status in statuses[-10:]:
                    errors.append(status[0]+' '+status[2])
                    for x in ['trust', 'itl']:
                        if x in status[2].lower():
                            phone_scrape_data.ITL =  status[2]
            phone_scrape_data.status =  errors

    # timestamp for last modified time
    phone_scrape_data.date_modified = datetime.now()

    return(phone_scrape_data)


def parse_7937_model(device_text: str, network_text:str) -> PhoneScraper:
    """Parse 7937 phone model web page

    Arguments:
        device_text {str} -- BS4 parsed requests response device page /localmenus.cgi?func=604  
        network_text {str} -- BS4 parsed requests response network page /localmenus.cgi?func=219

    Returns:
        PhoneScraper -- [description]
    """

    # ***** Device Parser *****
    if device_text != None:

        # Hostname parser & instantiate phonescraper object
        res = re.search(r'(Host Name : *)([^(_| )]*)', device_text)
        if res:
            temp_hostname = ""
            temp_hostname =  res.group(2).strip()
            phone_scrape_data = PhoneScraper(devicename=temp_hostname)
        else:
            raise NameError("Unable to locate hostname/devicename")

        # Other Device Parsers
        phone_scrape_data = regex_search_and_assign_if_match('sn', '(Serial Number: *)([^(_| |_\n)]*)', device_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('firmware', '(Software Version : *)([^_| ]*)', device_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dn', '(Phone DN : *)([^(_| )]*)', device_text, phone_scrape_data)
         
    # ***** Network Parser *****
    if network_text != None:
        phone_scrape_data = regex_search_and_assign_if_match('domain_name', '(Domain Name : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dhcp', '(DHCP Enabled : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('ip_address', '(IP Address : *)([^(_| )]*)', network_text, phone_scrape_data)      
        phone_scrape_data = regex_search_and_assign_if_match('subnetmask', '(Subnet Mask : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('gateway', '(Default Router 1 : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('dns1', '(DNS Server 1 : *)([^(_| )]*)', network_text, phone_scrape_data)      
        phone_scrape_data = regex_search_and_assign_if_match('dns2', '(DNS Server 2 : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('alt_tftp', '(Alternate TFTP : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('tftp1', '(TFTP Server 1 : *)([^(_| )]*)', network_text, phone_scrape_data)        
        phone_scrape_data = regex_search_and_assign_if_match('tftp2', '(TFTP Server 2 : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('op_vlan', '(Operational VLAN Id : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('admin_vlan', '(Admin. VLAN Id : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('cucm1', '(CallManager 1 : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm2', '(CallManager 2 : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm3', '(CallManager 3 : *|CallManager 3 SRST : *|CallManager 3 TFTP : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm4', '(CallManager 4 : *|CallManager 4 SRST : *|CallManager 4 TFTP : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm5', '(CallManager 5 : *|CallManager 5 SRST : *|CallManager 5 TFTP : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('info_url', '(Information URL : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dir_url', '(Directories URL : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('msg_url', '(Messages URL : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('svc_url', '(Services URL : *)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('idle_url', '(Idle URL : *)([^(_| )]*)', network_text, phone_scrape_data)      
        phone_scrape_data = regex_search_and_assign_if_match('info_url_time', '(Idle URL Time : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('proxy_url', '(Proxy Server URL : *)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('auth_url', '(Authentication URL : *)([^(_| )]*)', network_text, phone_scrape_data)

    # timestamp for last modified time
    phone_scrape_data.date_modified = datetime.now()
    phone_scrape_data.model = "7937"
    
    return(phone_scrape_data)


def parse_6901_model(model: str, device_text: str, network_text:str) -> PhoneScraper:
    """Parse 6901 phone model web page.  May also be used for other phones in 6900 series

    Arguments:
        model {str} -- model number of IP phone.  This function is for phones with webpages similiar to 6901
        device_text {str} -- BS4 parsed requests response device page /Device_Information.html 
        network_text {str} -- BS4 parsed requests response network page /Network_Setup.html

    Returns:
        PhoneScraper -- [description]
    """

    # TODO this is missing the 'URL' settings. Not sure if this phone model supports that
    # TODO this is missing the ITL value, not sure if this phone supports that.
    # TODO this is missing the CDP/LLDP values, not sure if this phone supports that.

    # ***** Device Parser *****
    if device_text != None:

        # Hostname parser & instantiate phonescraper object
        res = re.search(r'(Host Name_\n_\n_*)([^(_| )]*)', device_text)
        if res:
            temp_hostname = ""
            temp_hostname =  res.group(2).strip()
            phone_scrape_data = PhoneScraper(devicename=temp_hostname)
        else:
            raise NameError("Unable to locate hostname/devicename")

         # Other Device Parsers
        phone_scrape_data = regex_search_and_assign_if_match('sn', '(Serial Number_\n_\n_*)([^(_| |_\n)]*)', device_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('firmware', '(App Load ID_\n_\n_*)([^_| ]*)', device_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dn', '(Phone DN_\n_\n_*)([^(_| )]*)', device_text, phone_scrape_data)
         
    # ***** Network Parser *****
    if network_text != None:
        phone_scrape_data = regex_search_and_assign_if_match('domain_name', '(Domain Name_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dhcp', '(DHCP Enabled_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dhcp_server', '(DHCP Server_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('ip_address', '(IP Address_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('subnetmask', '(Subnet Mask_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('gateway', '(Default Router 1_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dns1', '(DNS Server 1_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dns2', '(DNS Server 2_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('alt_tftp', '(Alternate TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)       
        phone_scrape_data = regex_search_and_assign_if_match('tftp1', '(TFTP Server 1_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('tftp2', '(TFTP Server 2_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('op_vlan', '(Operational VLAN ID_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('admin_vlan', '(Admin VLAN ID_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm1', '(Unified CM 1_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)      
        phone_scrape_data = regex_search_and_assign_if_match('cucm2', '(Unified CM 2_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm3', '(Unified CM 3_\n_\xa0_\n_|Unified CM 3 SRST_\n_\xa0_\n_|Unified CM 3 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm4', '(Unified CM 4_\n_\xa0_\n_|Unified CM 4 SRST_\n_\xa0_\n_|Unified CM 4 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm5', '(Unified CM 5_\n_\xa0_\n_|Unified CM 5 SRST_\n_\xa0_\n_|Unified CM 5 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)

    # timestamp for last modified time
    phone_scrape_data.date_modified = datetime.now()
    phone_scrape_data.model = model

    return(phone_scrape_data)


def parse_ata187_model(model: str, device_text: str, network_text:str) -> PhoneScraper:
    """Parse ATA 187 phone model web page.

    Arguments:
        model {str} -- model number of IP phone.
        device_text {str} -- BS4 parsed requests response device page /Device_Information.html 
        network_text {str} -- BS4 parsed requests response network page /Network_Setup.html

    Returns:
        PhoneScraper -- [description]
    """

    # TODO this is missing the 'URL' settings. Not sure if this phone model supports that
    # TODO this is missing the ITL value, not sure if this phone supports that.
    # TODO this is missing the CDP/LLDP values, not sure if this phone supports that.

    # ***** Device Parser *****
    if device_text != None:

        # Hostname parser & instantiate phonescraper object
        # ATA doesn't actually have a hostname field in the webpage, so going to use MAC instead
        res = re.search(r'(MAC Address_\n_\n_)([^(_| )]*)', device_text)
        if res:
            temp_hostname = ""
            temp_hostname =  res.group(2).strip()
            temp_hostname = "SEP" + temp_hostname.replace(':','')  # Normalize hostname to same format as other models
            phone_scrape_data = PhoneScraper(devicename=temp_hostname)
        else:
            raise NameError("Unable to locate hostname/devicename")

         # Other Device Parsers
        phone_scrape_data = regex_search_and_assign_if_match('sn', '(Serial Number_\n_\n_)([^(_| |_\n)]*)', device_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('firmware', '(App Load ID_\n_\n_*)([^_| ]*)', device_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dn', '(Phone 1 DN_\n_\n_*)([^(_| )]*)', device_text, phone_scrape_data)
         
    # ***** Network Parser *****
    if network_text != None:
        phone_scrape_data = regex_search_and_assign_if_match('domain_name', '(Domain Name_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dhcp', '(DHCP Mode_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        if hasattr(phone_scrape_data, 'dhcp'):
            # Normalize value of dhcp to 'Yes' or 'No' to be like other phone models
            phone_scrape_data.dhcp =  "Yes" if phone_scrape_data.dhcp == "Enable" else "No"

        phone_scrape_data = regex_search_and_assign_if_match('dhcp_server', '(DHCP Server_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('ip_address', '(IP Address_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)      
        phone_scrape_data = regex_search_and_assign_if_match('subnetmask', '(Subnet Mask_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('gateway', '(Default Router 1_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('dns1', '(DNS Server 1_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)      
        phone_scrape_data = regex_search_and_assign_if_match('dns2', '(DNS Server 2_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('alt_tftp', '(Alternate Mode_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        if hasattr(phone_scrape_data, 'alt_tftp'):
            # Normalize value of Alt TFTP to 'Yes' or 'No' to be like other phone models
            phone_scrape_data.alt_tftp =  "Yes" if phone_scrape_data.alt_tftp == "Enable" else "No"
        
        phone_scrape_data = regex_search_and_assign_if_match('tftp1', '(TFTP Server 1_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('tftp2', '(TFTP Server 2_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('admin_vlan', '(Admin. VLAN ID_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm1', '(Call Manager 1_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm2', '(Call Manager 2_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm3', '(Call Manager 3_\n_\xa0_\n_|Call Manager 3 SRST_\n_\xa0_\n_|Call Manager 3 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm4', '(Call Manager 4_\n_\xa0_\n_|Call Manager 4 SRST_\n_\xa0_\n_|Call Manager 4 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)
        phone_scrape_data = regex_search_and_assign_if_match('cucm5', '(Call Manager 5_\n_\xa0_\n_|Call Manager 5 SRST_\n_\xa0_\n_|Call Manager 5 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text, phone_scrape_data)

    # timestamp for last modified time
    phone_scrape_data.date_modified = datetime.now()
    phone_scrape_data.model = model
    
    return(phone_scrape_data)


def allDetails(ip: str, model: str = None) -> PhoneScraper:
    """Use BeautifulSoup to scrape data from IP Phone built-in web server

    Arguments:
        ip {str} -- IP address of IP phone
        model {str} -- Model of IP phone (default: {None})

    Raises:
        ConnectionRefusedError: used if unable to reach phone web page (phone is off, web server turned off, ACL, etc)
        NameError: [description]

    Returns:
        PhoneScraper -- returns object
    """

    logger.debug(f"Starting scrape for model {model} at IP {ip}")

    # Determine URL based on model
    if model == "7940" or model == "7960":
        config_text = connect_to_phone("http://"+ip+"/NetworkConfiguration")
        device_text = connect_to_phone("http://"+ip+"/DeviceInformation")
        status_text = connect_to_phone("http://"+ip+"/DeviceLog?2")
        network_text = connect_to_phone("http://" + ip + "/PortInformation?1")
        phone_scrape_data = parse_standard_models(model, config_text, device_text, status_text, network_text)
    elif model == "6901":  ## TODO do we need to add 6911, 6921, 6961, etc ?
        device_text = connect_to_phone("http://"+ip+"/Device_Information.html")
        network_text = connect_to_phone("http://"+ip+"/Network_Setup.html")
        phone_scrape_data = parse_6901_model(model, device_text, network_text)
    elif model == "7937":
        device_text = connect_to_phone("http://"+ip+"/localmenus.cgi?func=604")
        network_text = connect_to_phone("http://"+ip+"/localmenus.cgi?func=219")
        phone_scrape_data = parse_7937_model(device_text, network_text)      
    elif model == "ATA 187":
        device_text = connect_to_phone("http://"+ip+"/Device_Information.htm")
        network_text = connect_to_phone("http://"+ip+"/Network_Setup.htm")
        phone_scrape_data = parse_ata187_model(model, device_text, network_text)
    else:
        # default URLs for most current phone models
        config_text = connect_to_phone("http://"+ip+"/CGI/Java/Serviceability?adapter=device.statistics.configuration")
        device_text = connect_to_phone("http://"+ip+"/CGI/Java/Serviceability?adapter=device.statistics.device")
        status_text = connect_to_phone("http://"+ip+"/CGI/Java/Serviceability?adapter=device.settings.status.messages")
        network_text = connect_to_phone("http://" + ip + "/CGI/Java/Serviceability?adapter=device.statistics.port.network")
        phone_scrape_data = parse_standard_models(model, config_text, device_text, status_text, network_text)
       
    return phone_scrape_data

if __name__ == "__main__":
    # used for debugging

    from pprint import pprint
    from api.crud import phone_data as crud


    def bs4_lxml(raw_text: str) -> str:
        soup_raw = BeautifulSoup(raw_text, features="lxml")
        soup_text = soup_raw.get_text('_')
        return soup_text

    # 8821 testing
    model = "8821"
    phone_scrape_data = None

    with open('/home/jsteinberg/test_files/8821/config.txt', 'r') as myfile:
        config_text = bs4_lxml(myfile.read())
    with open('/home/jsteinberg/test_files/8821/device.txt', 'r') as myfile:
        device_text = bs4_lxml(myfile.read())

    status_text = None
    network_text = None

    phone_scrape_data = parse_standard_models(model, config_text, device_text, status_text, network_text)

    pprint(vars(phone_scrape_data)) 
    crud.merge_phonescraper_data(phone_scrape_data)
    
    #7937 testing
    phone_scrape_data = None

    with open('/home/jsteinberg/test_files/7937/604.txt', 'r') as myfile:
        device_text = bs4_lxml(myfile.read())
    with open('/home/jsteinberg/test_files/7937/219.txt', 'r') as myfile:
        network_text = bs4_lxml(myfile.read())

    phone_scrape_data = parse_7937_model(device_text, network_text)

    pprint(vars(phone_scrape_data)) 
    crud.merge_phonescraper_data(phone_scrape_data)

    #6901 testing
    phone_scrape_data = None

    model = "6901"

    with open('/home/jsteinberg/test_files/6901/device.txt', 'r') as myfile:
        device_text = bs4_lxml(myfile.read())
    with open('/home/jsteinberg/test_files/6901/network.txt', 'r') as myfile:
        network_text = bs4_lxml(myfile.read())

    phone_scrape_data = parse_6901_model(model, device_text, network_text)

    pprint(vars(phone_scrape_data)) 
    crud.merge_phonescraper_data(phone_scrape_data)

    #ATA 187 testing
    phone_scrape_data = None

    model = "ATA 187"

    with open('/home/jsteinberg/test_files/ATA187/device.txt', 'r') as myfile:
        device_text = bs4_lxml(myfile.read())
    with open('/home/jsteinberg/test_files/ATA187/network.txt', 'r') as myfile:
        network_text = bs4_lxml(myfile.read())

    phone_scrape_data = parse_ata187_model(model, device_text, network_text)

    pprint(vars(phone_scrape_data)) 
    crud.merge_phonescraper_data(phone_scrape_data)

    # Requests testing

    phone_scrape_data = allDetails(ip = "163.118.100.119", model = "8811")
    crud.merge_phonescraper_data(phone_scrape_data)
