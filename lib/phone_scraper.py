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
        request response
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
    
    return response


def parse_standard_models(model: str, config_response: str, device_response: str, status_response: str, network_response: str) -> PhoneScraper:
    """Parse phone responses using BeautifulSoup

    Arguments:
        model {str} -- Cisco model number
        config_response {str} -- requests response from config URL
        device_response {str} -- requests response from device URL
        status_response {str} -- requests resposne from status URL
        network_response {str} -- requests response from network URL

    Raises:
        NameError: [description]

    Returns:
        PhoneScraper -- PhoneScraper model object
    """
    
    # ***** Config Parser *****
    if config_response != None:
        config_soup = BeautifulSoup(config_response.text, features="lxml")
        config_text = config_soup.get_text('_')

        # Hostname parser
        res = re.search(r'(Host Name_\n_\n_|Host name_|Host Name_)([^(_| )]*)', config_text)
        temp_hostname = ""
        if res:
            temp_hostname =  res.group(2).strip()
            phone_scrape_data = PhoneScraper(devicename=temp_hostname)
        else:
            raise NameError("Unable to locate hostname/devicename")

        # Domain Name parser
        res = re.search(r'(Domain Name_\n_\n_|Domain name_|Domain Name_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.domain_name =  res.group(2).strip()
        
        # DHCP parser
        res = re.search(r'(DHCP Server_\n_\n_|DHCP server_|DHCP Server_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.dhcp_server =  res.group(2).strip()
        res = re.search(r'(DHCP Enabled_\n_\n_|DHCP_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.dhcp =  res.group(2).strip()
        
        # IP Address / Network Info parser
        res = re.search(r'(IP Address_\n_\n_|IP address_|IP Address_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.ip_address =  res.group(2).strip()
        res = re.search(r'(Subnet Mask_\n_\n_|Subnet mask_|Subnet Mask_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.subnetmask =  res.group(2).strip()
        res = re.search(r'(Default Router 1_\n_\n_|Default router_|Default Router 1_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.gateway =  res.group(2).strip()
        
        # DNS parser
        res = re.search(r'(DNS Server 1_\n_\n_|DNS server 1_|DNS Server 1_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.dns1 =  res.group(2).strip()
        res = re.search(r'(DNS Server 2_\n_\n_|DNS server 2_|DNS Server 2_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.dns2 =  res.group(2).strip()

        # TFTP Info parser
        res = re.search(r'(Alternate TFTP_\n_\n_|Alternate TFTP_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.alt_tftp =  res.group(2).strip()
        res = re.search(r'(TFTP Server 1_\n_\n_|TFTP server 1_|TFTP Server 1_|TFTP Server 1)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.tftp1 =  res.group(2).strip()
        res = re.search(r'(TFTP Server 2_\n_\n_|TFTP server 2_|TFTP Server 2_|TFTP Server 2)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.tftp2 =  res.group(2).strip()
        
        # VLAN parser
        res = re.search(r'(Operational VLAN Id_\n_\n_|Operational VLAN ID_|Operational VLAN Id_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.op_vlan =  res.group(2).strip()
        res = re.search(r'(Admin. VLAN Id_\n_\n_|Admin VLAN ID_|Admin VLAN Id_)([^(_| )]*)',config_text)
        if res:
            phone_scrape_data.admin_vlan =  res.group(2).strip()
        
        # CUCM server parser
        if model == "8821":
            res = re.search(r'( Server 1_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm1 =  res.group(2).strip()
            res = re.search(r'( Server 2_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm2 =  res.group(2).strip()
            res = re.search(r'( Server 3_|Server 3 SRST_\n_\n_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm3 =  res.group(2).strip()
            res = re.search(r'( Server 4_|Server 4 SRST_\n_\n_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm4 =  res.group(2).strip()
            res = re.search(r'( Server 5_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm5 =  res.group(2).strip()
        else:
            res = re.search(r'(CUCM server1_|Unified CM 1_|CallManager 1_\n_\n_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm1 =  res.group(2).strip()
            res = re.search(r'(CUCM server2_|Unified CM 2_|CallManager 2_\n_\n_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm2 =  res.group(2).strip()
            res = re.search(r'(CUCM server3_|Unified CM 3_|CallManager 3_\n_\n_|CallManager 3 SRST_\n_\n_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm3 =  res.group(2).strip()
            res = re.search(r'(CUCM server4_|Unified CM 4_|CallManager 4_\n_\n_|CallManager 4 SRST_\n_\n_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm4 =  res.group(2).strip()
            res = re.search(r'(CUCM server5_|Unified CM 5_|CallManager 5_\n_\n_)([^(_| )]*)', config_text)
            if res:
                phone_scrape_data.cucm5 =  res.group(2).strip()

        # URL parser
        res = re.search(r'(Information URL_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.info_url =  res.group(2).strip()
        res = re.search(r'(Directories URL_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.dir_url =  res.group(2).strip()
        res = re.search(r'(Messages URL_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.msg_url =  res.group(2).strip()
        res = re.search(r'(Services URL_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.svc_url =  res.group(2).strip()
        res = re.search(r'(Idle URL_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.idle_url =  res.group(2).strip()
        res = re.search(r'(Idle URL time_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.info_url_time =  res.group(2).strip()
        res = re.search(r'(Proxy Server URL_|Proxy server URL)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.proxy_url =  res.group(2).strip()
        res = re.search(r'(Authentication URL_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.auth_url =  res.group(2).strip()
        
        # TVS parser
        res = re.search(r'(TVS_)([^(_| )]*)', config_text)
        if res:
            phone_scrape_data.tvs =  res.group(2).strip()


    # ***** Device Parser *****
    if device_response != None:

        device_soup = BeautifulSoup(device_response.text, features="lxml")
        device_text = device_soup.get_text('_')

        # Serial Number parser
        res = re.search(r'(Serial Number_\n_\n_|Serial number_|Serial Number_)([^(_| |_\n)]*)', device_text)
        if res:
            phone_scrape_data.sn = res.group(2).strip()
        
        # Firmware Version parser
        res = re.search(r'(Version__\n_\n_|Version_)([^(_| )]*)', device_text)
        if res:
            phone_scrape_data.firmware = res.group(2).strip()
        
        # Phone Directory Number 1 parser
        res = re.search(r'(Phone DN_\n_\n_|Phone DN_)([^(_| )]*)', device_text)
        if res:
            phone_scrape_data.dn =  res.group(2).strip()
        
        # Model Number parser
        res = re.search(r'(Model Number_\n_\n_|Model number_|Model Number_)([^(_| )]*)', device_text)
        if res:
            phone_scrape_data.model = res.group(2).strip()
            if 'CP' in phone_scrape_data.model:
                phone_scrape_data.model =  phone_scrape_data.model.replace('CP-', '')

            if 'G' in phone_scrape_data.model:
                if phone_scrape_data.model[-1] == "G": phone_scrape_data.model =  phone_scrape_data.model[:-1] # remove G from the end if it is the last character
        
        # KEM parser
        res = re.search(r'(Key expansion module 1_|Key Expansion Module 1_)([^(_| )]*)', device_text)
        if res:
            phone_scrape_data.kem1 =  res.group(2).strip()
        res = re.search(r'(Key expansion module 2_|Key Expansion Module 2_)([^(_| )]*)', device_text)
        if res:
            phone_scrape_data.kem2 =  res.group(2).strip()

    # ***** Network Parser *****
    if network_response != None:
        network_soup = BeautifulSoup(network_response.text, features="lxml")
        network_text = network_soup.get_text('_')
        
        # CDP/LLDP Network parser
        res = re.search(r'(Neighbor Device ID_\n_\n_|CDP Neighbor device ID_|CDP Neighbor Device ID_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.CDP_Neighbor_ID =  res.group(2).strip()

        res = re.search(r'(Neighbor IP Address_\n_\n_|CDP Neighbor IP address_|CDP Neighbor IP Address_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.CDP_Neighbor_IP =  res.group(2).strip()

        res = re.search(r'(Neighbor Port_\n_\n_|CDP Neighbor Port_|CDP Neighbor port_)([^_]*)', network_text)
        if res:
            phone_scrape_data.CDP_Neighbor_Port =  res.group(2).strip()

        res = re.search(r'(LLDP Neighbor Device ID_|LLDP Neighbor device ID_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.LLDP_Neighbor_ID =  res.group(2).strip()

        res = re.search(r'(LLDP Neighbor IP Address_|LLDP Neighbor IP address_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.LLDP_Neighbor_IP =  res.group(2).strip()

        res = re.search(r'(LLDP Neighbor Port_|LLDP Neighbor port_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.LLDP_Neighbor_Port =  res.group(2).strip()

    
    # Status parser (includes ITL)
    if status_response != None:
        status_soup = BeautifulSoup(status_response.text, features="lxml")
        status_text = status_soup.get_text('_')

        
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


def parse_7937_model(device_response: str, network_response:str) -> PhoneScraper:
    """Parse 7937 phone model web page

    Arguments:
        device_response {str} -- device page /localmenus.cgi?func=604  
        network_response {str} -- network page /localmenus.cgi?func=219

    Returns:
        PhoneScraper -- [description]
    """

    # ***** Device Parser *****
    if device_response != None:
        device_soup = BeautifulSoup(device_response.text, features="lxml")
        device_text = device_soup.get_text('_')

        # Hostname parser
        res = re.search(r'(Host Name : *)([^(_| )]*)', device_text)
        temp_hostname = ""
        if res:
            temp_hostname =  res.group(2).strip()
            phone_scrape_data = PhoneScraper(devicename=temp_hostname)
        else:
            raise NameError("Unable to locate hostname/devicename")

         # Serial Number parser
        res = re.search(r'(Serial Number: *)([^(_| |_\n)]*)', device_text)
        if res:
            phone_scrape_data.sn = res.group(2).strip()
        
        # Firmware Version parser
        res = re.search(r'(Software Version : *)([^_| ]*)', device_text)
        if res:
            phone_scrape_data.firmware = res.group(2).strip()
        
        # Phone Directory Number 1 parser
        res = re.search(r'(Phone DN : *)([^(_| )]*)', device_text)
        if res:
            phone_scrape_data.dn =  res.group(2).strip()
         
    # ***** Network Parser *****
    if network_response != None:
        network_soup = BeautifulSoup(network_response.text, features="lxml")
        network_text = network_soup.get_text('_')


        # Domain Name parser
        res = re.search(r'(Domain Name : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.domain_name =  res.group(2).strip()
        
        # DHCP parser
        res = re.search(r'(DHCP Enabled : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dhcp =  res.group(2).strip()
        
        # IP Address / Network Info parser
        res = re.search(r'(IP Address : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.ip_address =  res.group(2).strip()
        res = re.search(r'(Subnet Mask : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.subnetmask =  res.group(2).strip()
        res = re.search(r'(Default Router 1 : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.gateway =  res.group(2).strip()
        
        # DNS parser
        res = re.search(r'(DNS Server 1 : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dns1 =  res.group(2).strip()
        res = re.search(r'(DNS Server 2 : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dns2 =  res.group(2).strip()

        # TFTP Info parser
        res = re.search(r'(Alternate TFTP : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.alt_tftp =  res.group(2).strip()
        res = re.search(r'(TFTP Server 1 : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.tftp1 =  res.group(2).strip()
        res = re.search(r'(TFTP Server 2 : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.tftp2 =  res.group(2).strip()
        
        # VLAN parser
        res = re.search(r'(Operational VLAN Id : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.op_vlan =  res.group(2).strip()
        res = re.search(r'(Admin. VLAN Id : *)([^(_| )]*)',network_text)
        if res:
            phone_scrape_data.admin_vlan =  res.group(2).strip()
        
        # CUCM server parser

        res = re.search(r'(CallManager 1 : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm1 =  res.group(2).strip()
        res = re.search(r'(CallManager 2 : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm2 =  res.group(2).strip()
        res = re.search(r'(CallManager 3 : *|CallManager 3 SRST : *|CallManager 3 TFTP : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm3 =  res.group(2).strip()
        res = re.search(r'(CallManager 4 : *|CallManager 4 SRST : *|CallManager 4 TFTP : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm4 =  res.group(2).strip()
        res = re.search(r'(CallManager 5 : *|CallManager 5 SRST : *|CallManager 5 TFTP : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm5 =  res.group(2).strip()

        # URL parser
        res = re.search(r'(Information URL : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.info_url =  res.group(2).strip()
        res = re.search(r'(Directories URL : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dir_url =  res.group(2).strip()
        res = re.search(r'(Messages URL : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.msg_url =  res.group(2).strip()
        res = re.search(r'(Services URL : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.svc_url =  res.group(2).strip()
        res = re.search(r'(Idle URL : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.idle_url =  res.group(2).strip()
        res = re.search(r'(Idle URL Time : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.info_url_time =  res.group(2).strip()
        res = re.search(r'(Proxy Server URL : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.proxy_url =  res.group(2).strip()
        res = re.search(r'(Authentication URL : *)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.auth_url =  res.group(2).strip()


    # timestamp for last modified time
    phone_scrape_data.date_modified = datetime.now()
    phone_scrape_data.model = "7937"
    

    return(phone_scrape_data)


def parse_6901_model(model: str, device_response: str, network_response:str) -> PhoneScraper:
    """Parse 6901 phone model web page.  May also be used for other phones in 6900 series

    Arguments:
        model {str} -- model number of IP phone.  This function is for phones with webpages similiar to 6901
        device_response {str} -- device page /Device_Information.html 
        network_response {str} -- network page /Network_Setup.html

    Returns:
        PhoneScraper -- [description]
    """

    # TODO this is missing the 'URL' settings. Not sure if this phone model supports that
    # TODO this is missing the ITL value, not sure if this phone supports that.
    # TODO this is missing the CDP/LLDP values, not sure if this phone supports that.

    # ***** Device Parser *****
    if device_response != None:
        device_soup = BeautifulSoup(device_response.text, features="lxml")
        device_text = device_soup.get_text('_')

        # Hostname parser
        res = re.search(r'(Host Name_\n_\n_*)([^(_| )]*)', device_text)
        temp_hostname = ""
        if res:
            temp_hostname =  res.group(2).strip()
            phone_scrape_data = PhoneScraper(devicename=temp_hostname)
        else:
            raise NameError("Unable to locate hostname/devicename")

         # Serial Number parser
        res = re.search(r'(Serial Number_\n_\n_*)([^(_| |_\n)]*)', device_text)
        if res:
            phone_scrape_data.sn = res.group(2).strip()
        
        # Firmware Version parser
        res = re.search(r'(App Load ID_\n_\n_*)([^_| ]*)', device_text)
        if res:
            phone_scrape_data.firmware = res.group(2).strip()
        
        # Phone Directory Number 1 parser
        res = re.search(r'(Phone DN_\n_\n_*)([^(_| )]*)', device_text)
        if res:
            phone_scrape_data.dn =  res.group(2).strip()
         
    # ***** Network Parser *****
    if network_response != None:
        network_soup = BeautifulSoup(network_response.text, features="lxml")
        network_text = network_soup.get_text('_')


        # Domain Name parser
        res = re.search(r'(Domain Name_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.domain_name =  res.group(2).strip()
        
        # DHCP parser
        res = re.search(r'(DHCP Enabled_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dhcp =  res.group(2).strip()

        res = re.search(r'(DHCP Server_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dhcp_server =  res.group(2).strip()
        
        # IP Address / Network Info parser
        res = re.search(r'(IP Address_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.ip_address =  res.group(2).strip()
        res = re.search(r'(Subnet Mask_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.subnetmask =  res.group(2).strip()
        res = re.search(r'(Default Router 1_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.gateway =  res.group(2).strip()
        
        # DNS parser
        res = re.search(r'(DNS Server 1_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dns1 =  res.group(2).strip()
        res = re.search(r'(DNS Server 2_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dns2 =  res.group(2).strip()

        # TFTP Info parser
        res = re.search(r'(Alternate TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.alt_tftp =  res.group(2).strip()
        res = re.search(r'(TFTP Server 1_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.tftp1 =  res.group(2).strip()
        res = re.search(r'(TFTP Server 2_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.tftp2 =  res.group(2).strip()
        
        # VLAN parser
        res = re.search(r'(Operational VLAN ID_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.op_vlan =  res.group(2).strip()
        res = re.search(r'(Admin VLAN ID_\n_\xa0_\n_)([^(_| )]*)',network_text)
        if res:
            phone_scrape_data.admin_vlan =  res.group(2).strip()
        
        # CUCM server parser

        res = re.search(r'(Unified CM 1_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm1 =  res.group(2).strip()
        res = re.search(r'(Unified CM 2_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm2 =  res.group(2).strip()
        res = re.search(r'(Unified CM 3_\n_\xa0_\n_|Unified CM 3 SRST_\n_\xa0_\n_|Unified CM 3 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm3 =  res.group(2).strip()
        res = re.search(r'(Unified CM 4_\n_\xa0_\n_|Unified CM 4 SRST_\n_\xa0_\n_|Unified CM 4 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm4 =  res.group(2).strip()
        res = re.search(r'(Unified CM 5_\n_\xa0_\n_|Unified CM 5 SRST_\n_\xa0_\n_|Unified CM 5 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm5 =  res.group(2).strip()

    # timestamp for last modified time
    phone_scrape_data.date_modified = datetime.now()
    phone_scrape_data.model = model
    

    return(phone_scrape_data)


def parse_ata187_model(model: str, device_response: str, network_response:str) -> PhoneScraper:
    """Parse ATA 187 phone model web page.

    Arguments:
        model {str} -- model number of IP phone.
        device_response {str} -- device page /Device_Information.html 
        network_response {str} -- network page /Network_Setup.html

    Returns:
        PhoneScraper -- [description]
    """

    # TODO this is missing the 'URL' settings. Not sure if this phone model supports that
    # TODO this is missing the ITL value, not sure if this phone supports that.
    # TODO this is missing the CDP/LLDP values, not sure if this phone supports that.

    # ***** Device Parser *****
    if device_response != None:
        device_soup = BeautifulSoup(device_response.text, features="lxml")
        device_text = device_soup.get_text('_')

        # Hostname parser  # ATA doesn't actually have a hostname field in the webpage, so going to use MAC instead
        res = re.search(r'(MAC Address_\n_\n_)([^(_| )]*)', device_text)
        temp_hostname = ""
        if res:
            temp_hostname =  res.group(2).strip()
            temp_hostname = "SEP" + temp_hostname.replace(':','')
            phone_scrape_data = PhoneScraper(devicename=temp_hostname)
        else:
            raise NameError("Unable to locate hostname/devicename")

         # Serial Number parser
        res = re.search(r'(Serial Number_\n_\n_)([^(_| |_\n)]*)', device_text)
        if res:
            phone_scrape_data.sn = res.group(2).strip()
        
        # Firmware Version parser
        res = re.search(r'(App Load ID_\n_\n_*)([^_| ]*)', device_text)
        if res:
            phone_scrape_data.firmware = res.group(2).strip()
        
        # Phone Directory Number 1 parser
        res = re.search(r'(Phone 1 DN_\n_\n_*)([^(_| )]*)', device_text)
        if res:
            phone_scrape_data.dn =  res.group(2).strip()
         
    # ***** Network Parser *****
    if network_response != None:
        network_soup = BeautifulSoup(network_response.text, features="lxml")
        network_text = network_soup.get_text('_')


        # Domain Name parser
        res = re.search(r'(Domain Name_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.domain_name =  res.group(2).strip()
        
        # DHCP parser
        res = re.search(r'(DHCP Mode_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dhcp =  "Yes" if res.group(2).strip() == "Enable" else "No"

        res = re.search(r'(DHCP Server_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dhcp_server =  res.group(2).strip()
        
        # IP Address / Network Info parser
        res = re.search(r'(IP Address_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.ip_address =  res.group(2).strip()
        res = re.search(r'(Subnet Mask_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.subnetmask =  res.group(2).strip()
        res = re.search(r'(Default Router 1_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.gateway =  res.group(2).strip()
        
        # DNS parser
        res = re.search(r'(DNS Server 1_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dns1 =  res.group(2).strip()
        res = re.search(r'(DNS Server 2_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.dns2 =  res.group(2).strip()

        # TFTP Info parser
        res = re.search(r'(Alternate Mode_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.alt_tftp =  "Yes" if res.group(2).strip() == "Enable" else "No"
        res = re.search(r'(TFTP Server 1_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.tftp1 =  res.group(2).strip()
        res = re.search(r'(TFTP Server 2_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.tftp2 =  res.group(2).strip()
        
        # VLAN parser
        res = re.search(r'(Admin. VLAN ID_\n_\xa0_\n_)([^(_| )]*)',network_text)
        if res:
            phone_scrape_data.admin_vlan =  res.group(2).strip()
        
        # CUCM server parser

        res = re.search(r'(Call Manager 1_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm1 =  res.group(2).strip()
        res = re.search(r'(Call Manager 2_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm2 =  res.group(2).strip()
        res = re.search(r'(Call Manager 3_\n_\xa0_\n_|Call Manager 3 SRST_\n_\xa0_\n_|Call Manager 3 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm3 =  res.group(2).strip()
        res = re.search(r'(Call Manager 4_\n_\xa0_\n_|Call Manager 4 SRST_\n_\xa0_\n_|Call Manager 4 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm4 =  res.group(2).strip()
        res = re.search(r'(Call Manager 5_\n_\xa0_\n_|Call Manager 5 SRST_\n_\xa0_\n_|Call Manager 5 TFTP_\n_\xa0_\n_)([^(_| )]*)', network_text)
        if res:
            phone_scrape_data.cucm5 =  res.group(2).strip()

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
        config_response = connect_to_phone("http://"+ip+"/NetworkConfiguration")
        device_response = connect_to_phone("http://"+ip+"/DeviceInformation")
        status_response = connect_to_phone("http://"+ip+"/DeviceLog?2")
        network_response = connect_to_phone("http://" + ip + "/PortInformation?1")
        phone_scrape_data = parse_standard_models(model, config_response, device_response, status_response, network_response)
    elif model == "6901":  ## TODO do we need to add 6911, 6921, 6961, etc ?
        device_response = connect_to_phone("http://"+ip+"/Device_Information.html")
        network_response = connect_to_phone("http://"+ip+"/Network_Setup.html")
        phone_scrape_data = parse_6901_model(model, device_response, network_response)
    elif model == "7937":
        device_response = connect_to_phone("http://"+ip+"/localmenus.cgi?func=604")
        network_response = connect_to_phone("http://"+ip+"/localmenus.cgi?func=219")
        phone_scrape_data = parse_7937_model(device_response, network_response)      
    elif model == "ATA 187":
        device_response = connect_to_phone("http://"+ip+"/Device_Information.htm")
        network_response = connect_to_phone("http://"+ip+"/Network_Setup.htm")
        phone_scrape_data = parse_ata187_model(model, device_response, network_response)
    else:
        # default URLs for most current phone models
        config_response = connect_to_phone("http://"+ip+"/CGI/Java/Serviceability?adapter=device.statistics.configuration")
        device_response = connect_to_phone("http://"+ip+"/CGI/Java/Serviceability?adapter=device.statistics.device")
        status_response = connect_to_phone("http://"+ip+"/CGI/Java/Serviceability?adapter=device.settings.status.messages")
        network_response = connect_to_phone("http://" + ip + "/CGI/Java/Serviceability?adapter=device.statistics.port.network")
        phone_scrape_data = parse_standard_models(model, config_response, device_response, status_response, network_response)
       
    return phone_scrape_data

if __name__ == "__main__":
    # used for debugging

    class Object(object):
        pass

    from pprint import pprint
    from api.crud import phone_data as crud


    # 8821 testing
    model = "8821"
    config_response = Object()
    device_response = Object()
    phone_scrape_data = None

    with open('/home/jsteinberg/test_files/8821/config.txt', 'r') as myfile:
        config_response.text = myfile.read()
    with open('/home/jsteinberg/test_files/8821/device.txt', 'r') as myfile:
        device_response.text = myfile.read()

    status_response = None
    network_response = None

    phone_scrape_data = parse_standard_models(model, config_response, device_response, status_response, network_response)

    pprint(vars(phone_scrape_data)) 
    crud.merge_phonescraper_data(phone_scrape_data)
    
    #7937 testing
    device_response = Object()
    network_response = Object()
    phone_scrape_data = None

    with open('/home/jsteinberg/test_files/7937/604.txt', 'r') as myfile:
        device_response.text = myfile.read()
    with open('/home/jsteinberg/test_files/7937/219.txt', 'r') as myfile:
        network_response.text = myfile.read()

    phone_scrape_data = parse_7937_model(device_response, network_response)

    pprint(vars(phone_scrape_data)) 
    crud.merge_phonescraper_data(phone_scrape_data)

    #6901 testing
    device_response = Object()
    network_response = Object()
    phone_scrape_data = None

    model = "6901"

    with open('/home/jsteinberg/test_files/6901/device.txt', 'r') as myfile:
        device_response.text = myfile.read()
    with open('/home/jsteinberg/test_files/6901/network.txt', 'r') as myfile:
        network_response.text = myfile.read()

    phone_scrape_data = parse_6901_model(model, device_response, network_response)

    pprint(vars(phone_scrape_data)) 
    crud.merge_phonescraper_data(phone_scrape_data)

    #ATA 187 testing
    device_response = Object()
    network_response = Object()
    phone_scrape_data = None

    model = "ATA 187"

    with open('/home/jsteinberg/test_files/ATA187/device.txt', 'r') as myfile:
        device_response.text = myfile.read()
    with open('/home/jsteinberg/test_files/ATA187/network.txt', 'r') as myfile:
        network_response.text = myfile.read()

    phone_scrape_data = parse_ata187_model(model, device_response, network_response)

    pprint(vars(phone_scrape_data)) 
    crud.merge_phonescraper_data(phone_scrape_data)