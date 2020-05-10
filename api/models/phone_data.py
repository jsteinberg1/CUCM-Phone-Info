from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from api.db.database import Base

current_time = datetime.now()

class Phone(Base):
    """Model used to store AXL/Serviceability data into SQL database"""
    __tablename__ = "phone"
    
    # Serviceability Fields    
    devicename = Column(String, primary_key=True, index=True)
    firmware	= Column(String)
    ipv4	= Column(String)
    first_seen_reg	= Column(DateTime, default=current_time)
    last_seen_reg = Column(DateTime, default=current_time)
    registration_time	= Column(DateTime)
    cluster	= Column(String)
    Protocol	= Column(String)
    Model	= Column(String)

    # AXL Fields
    devicepool = Column(String)
    devicecss	= Column(String)
    description	= Column(String)
    em_profile	= Column(String)
    em_time	= Column(DateTime)

    phonescrape = relationship("PhoneScraper", uselist=False, back_populates="phone")

class PhoneScraper(Base):
    """Model used to store data scraped from IP Phone web server into SQL database"""
    __tablename__ = "phonescraper"

    devicename = Column(String, ForeignKey("phone.devicename"),  primary_key=True)
    sn = Column(String, unique=True)
    firmware = Column(String)
    dn = Column(String)
    model = Column(String)
    kem1 = Column(String)
    kem2 = Column(String)
    domain_name = Column(String)
    dhcp_server = Column(String)
    dhcp = Column(String)
    ip_address = Column(String)
    subnetmask = Column(String)
    gateway = Column(String)
    dns1 = Column(String)
    dns2 = Column(String)
    alt_tftp = Column(String)
    tftp1 = Column(String)
    tftp2 = Column(String)
    op_vlan = Column(String)
    admin_vlan = Column(String)
    cucm1 = Column(String)
    cucm2 = Column(String)
    cucm3 = Column(String)
    cucm4 = Column(String)
    cucm5 = Column(String)
    info_url = Column(String)
    dir_url = Column(String)
    msg_url = Column(String)
    svc_url = Column(String)
    idle_url = Column(String)
    info_url_time = Column(String)
    proxy_url = Column(String)
    auth_url = Column(String)
    tvs = Column(String)
    CDP_Neighbor_ID = Column(String)
    CDP_Neighbor_IP = Column(String)
    CDP_Neighbor_Port = Column(String)
    LLDP_Neighbor_ID = Column(String)
    LLDP_Neighbor_IP = Column(String)
    LLDP_Neighbor_Port = Column(String)
    ITL = Column(String)
    date_modified = Column(DateTime)

    phone = relationship("Phone", back_populates="phonescrape")


class JobStatus(Base):
    """Model used to store data about CUCM/PHone scrape job sync/task statuses"""
    __bind_key__ = 'syncdata'
    __tablename__ = "jobstatus"
    jobname = Column(String, primary_key=True, index=True)
    laststarttime = Column(String)
    result = Column(String)