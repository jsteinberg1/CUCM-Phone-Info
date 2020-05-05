from datetime import datetime
from typing import List

from pydantic import BaseModel

# phone scraper will not be used as a schema, because Fastapi won't be updates to update this data.  leaving here as example.

class PhoneInfo(BaseModel):
    # Serviceability fields

    dname: str
    fw: str = None
    ipv4: str = None
    fdate: str = None
    ldate: str = None
    regstamp: str = None
    cluster: str = None
    prot: str = None
    model: str = None

    # AXL Fields

    dpool: str = None
    dcss: str = None
    descr: str = None
    em_profile: str = None
    em_time: str = None


class PhoneScraper(BaseModel):
    devicename: str = None
    sn: str = None
    firmware: str = None
    dn: str = None
    model: str = None
    kem1: str = None
    kem2: str = None
    domain_name: str = None
    dhcp_server: str = None
    dhcp: str = None
    ip_address: str = None
    subnetmask: str = None
    gateway: str = None
    dns1: str = None
    dns2: str = None
    alt_tftp: str = None
    tftp1: str = None
    tftp2: str = None
    op_vlan: str = None
    admin_vlan: str = None
    cucm1: str = None
    cucm2: str = None
    cucm3: str = None
    cucm4: str = None
    cucm5: str = None
    info_url: str = None
    dir_url: str = None
    msg_url: str = None
    svc_url: str = None
    idle_url: str = None
    info_url_time: str = None
    proxy_url: str = None
    auth_url: str = None
    tvs: str = None
    CDP_Neighbor_ID: str = None
    CDP_Neighbor_IP: str = None
    CDP_Neighbor_Port: str = None
    LLDP_Neighbor_ID: str = None
    LLDP_Neighbor_IP: str = None
    LLDP_Neighbor_Port: str = None
    ITL: str = None
    date_modified: str = None