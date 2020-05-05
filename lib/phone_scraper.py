import os
import subprocess
import platform
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

from api.models.phone_data import PhoneScraper


def allDetails(ip: str, model: str = None):
    
    current_time = datetime.now()
    headers = {}
    requests_time = 3
    config_url = "http://"+ip+"/CGI/Java/Serviceability?adapter=device.statistics.configuration"
    device_url = "http://"+ip+"/CGI/Java/Serviceability?adapter=device.statistics.device"
    status_url = "http://"+ip+"/CGI/Java/Serviceability?adapter=device.settings.status.messages"
    network_url = "http://" + ip + "/CGI/Java/Serviceability?adapter=device.statistics.port.network"

    # special phone models

    # Handle old models
    if model == "7940" or model == "7960":
        config_url = "http://"+ip+"/NetworkConfiguration"
        device_url = "http://"+ip+"/DeviceInformation"
        status_url = "http://"+ip+"/DeviceLog?2"
        network_url = "http://" + ip + "/PortInformation?1"
        

    try:
        config_response = requests.request("GET", config_url, headers=headers, timeout=requests_time)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise ConnectionRefusedError(f"unable to connect {e} - {config_url}")

    try:
        device_response = requests.request("GET", device_url, headers=headers, timeout=requests_time)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise ConnectionRefusedError(f"unable to connect {e} - {device_url}")

    try:
        status_response = requests.request("GET", status_url, headers=headers, timeout=requests_time)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise ConnectionRefusedError(f"unable to connect {e} - {status_url}")

    try:
        network_response = requests.request("GET", network_url, headers=headers, timeout=requests_time)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise ConnectionRefusedError(f"unable to connect {e} - {network_url}")

    config_soup = BeautifulSoup(config_response.text, features="lxml")
    config_text = config_soup.get_text('_')

    device_soup = BeautifulSoup(device_response.text, features="lxml")
    device_text = device_soup.get_text('_')

    status_soup = BeautifulSoup(status_response.text, features="lxml")
    status_text = status_soup.get_text('_')

    network_soup = BeautifulSoup(network_response.text, features="lxml")
    network_text = network_soup.get_text('_')

    res = re.search(r'(Host Name_\n_\n_|Host name_|Host Name_)([^(_| )]*)', config_text)
    temp_hostname = ""
    if res:
        temp_hostname =  res.group(2).strip()
        phone_scrape_data = PhoneScraper(devicename=temp_hostname)
    else:
        raise NameError("Unable to locate hostname/devicename")

    res = re.search(r'(Serial Number_\n_\n_|Serial number_|Serial Number_)([^(_| |_\n)]*)', device_text)
    if res:
        phone_scrape_data.sn = res.group(2).strip()
    res = re.search(r'(Version__\n_\n_|Version_)([^(_| )]*)', device_text)
    if res:
        phone_scrape_data.firmware = res.group(2).strip()
    res = re.search(r'(Phone DN_\n_\n_|Phone DN_)([^(_| )]*)', device_text)
    if res:
        phone_scrape_data.dn =  res.group(2).strip()
    res = re.search(r'(Model Number_\n_\n_|Model number_|Model Number_)([^(_| )]*)', device_text)
    if res:
        phone_scrape_data.model = res.group(2).strip()
        if 'CP' in phone_scrape_data.model:
            phone_scrape_data.model =  phone_scrape_data.model.replace('CP-', '')

        if 'G' in phone_scrape_data.model:
            if phone_scrape_data.model[-1] == "G": phone_scrape_data.model =  phone_scrape_data.model[:-1] # remove G from the end if it is the last character
    
    res = re.search(r'(Key expansion module 1_|Key Expansion Module 1_)([^(_| )]*)', device_text)
    if res:
        phone_scrape_data.kem1 =  res.group(2).strip()
    res = re.search(r'(Key expansion module 2_|Key Expansion Module 2_)([^(_| )]*)', device_text)
    if res:
        phone_scrape_data.kem2 =  res.group(2).strip()
    res = re.search(r'(Domain Name_\n_\n_|Domain name_|Domain Name_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.domain_name =  res.group(2).strip()
    res = re.search(r'(DHCP Server_\n_\n_|DHCP server_|DHCP Server_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.dhcp_server =  res.group(2).strip()
    res = re.search(r'(DHCP Enabled_\n_\n_|DHCP_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.dhcp =  res.group(2).strip()
    res = re.search(r'(IP Address_\n_\n_|IP address_|IP Address_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.ip_address =  res.group(2).strip()
    res = re.search(r'(Subnet Mask_\n_\n_|Subnet mask_|Subnet Mask_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.subnetmask =  res.group(2).strip()
    res = re.search(r'(Default Router 1_\n_\n_|Default router_|Default Router 1_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.gateway =  res.group(2).strip()
    res = re.search(r'(DNS Server 1_\n_\n_|DNS server 1_|DNS Server 1_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.dns1 =  res.group(2).strip()
    res = re.search(r'(DNS Server 2_\n_\n_|DNS server 2_|DNS Server 2_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.dns2 =  res.group(2).strip()
    res = re.search(r'(Alternate TFTP_\n_\n_|Alternate TFTP_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.alt_tftp =  res.group(2).strip()
    res = re.search(r'(TFTP Server 1_\n_\n_|TFTP server 1_|TFTP Server 1_|TFTP Server 1)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.tftp1 =  res.group(2).strip()
    res = re.search(r'(TFTP Server 2_\n_\n_|TFTP server 2_|TFTP Server 2_|TFTP Server 2)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.tftp2 =  res.group(2).strip()
    res = re.search(r'(Operational VLAN Id_\n_\n_|Operational VLAN ID_|Operational VLAN Id_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.op_vlan =  res.group(2).strip()
    res = re.search(r'(Admin. VLAN Id_\n_\n_|Admin VLAN ID_|Admin VLAN Id_)([^(_| )]*)',config_text)
    if res:
        phone_scrape_data.admin_vlan =  res.group(2).strip()
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
    res = re.search(r'(TVS_)([^(_| )]*)', config_text)
    if res:
        phone_scrape_data.tvs =  res.group(2).strip()

    #Network parsing
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


    # Status varies based on model
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

    phone_scrape_data.date_modified = current_time

    return(phone_scrape_data)


def itlCheck(phone):
    ITL = ''
    date = ''
    mac = ''
    model= ''
    TFTP = ''
    headers = {}
    requests_time = 1
    status_url = "http://" + phone + "/CGI/Java/Serviceability?adapter=device.settings.status.messages"


    try:
        status_response = requests.request("GET", status_url, headers=headers, timeout=requests_time)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        raise (f"unable to connect to {phone}")


    status_soup = BeautifulSoup(status_response.text, features="lxml")
    status_text = status_soup.get_text('_')

    mac = re.findall('( SEP.{12} )', status_text)
    if len(mac) == 1: mac = mac[0].strip()

    model = re.findall('CP-\d{4}', status_text)
    if len(model)==1: # only one model found
        model = model[0].replace('CP-','')

    if model in ['7962','7942']:
        statuses = (re.findall(r'(\d{1,2}:..:..[ap]) ([^(_)]*)', status_text))
        for status in statuses:
            for x in ['trust', 'itl']:
                if x in status[1].lower():
                    ITL = status[1]
                    date = status[0]
            if 'tftp' in status[1].lower():
                TFTP = status[1]
    else:
        statuses = re.findall(r'(..:..:...m ..\/..\/...)(\n)([^(_)]*)', status_text)
        for status in statuses:
            for x in ['trust', 'itl']:
                if x in status[2].lower():
                    ITL = status[2]
                    date = status[0]
            if 'tftp' in status[2].lower():
                TFTP = status[2]

    return mac, model, ITL, TFTP, date



if __name__ == "__main__":
    phone = "10.99.70.213"
    result = allDetails(ip=phone, model="8831")
    print(result.ITL)