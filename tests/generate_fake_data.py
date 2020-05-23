import random
from datetime import datetime, timedelta
from ipaddress import IPv4Address

from api.models import phone_data as models
from api.crud import phone_data as crud

# Generate fake data to insert into DB
number_of_fake_phones = 30000

model_phone_list = []
model_phonescraper_list = []

for count in range(number_of_fake_phones):

    site = random.choice(['HQ', 'Remote 1', 'Remote 2'])
    temp_model = random.choice(['7941', '7961', '8811', '8841', '8851', '7937', '8831'])
    temp_ip = str(IPv4Address(random.getrandbits(32)))

    # Phone model
    model_phone = models.Phone(
        # Serviceability Fields

        devicename = 'SEP' + str(count).zfill(12),
        firmware = 'FW API' + str(count),
        ipv4 = temp_ip,
        first_seen_reg	= datetime.now() - timedelta(days=random.choice(range(60,90))),
        last_seen_reg = datetime.now(),
        registration_time = datetime.now() - timedelta(days=random.choice(range(30))),
        cluster	= "test",
        Protocol	= random.choice(['SIP', 'SCCP']),
        Model	= temp_model,

        # AXL Fields
        devicepool = site + " DP",
        devicecss	= site + " CSS",
        description	= "Test Phone - " + str(count),
        em_profile	= "UDP_" + str(count).zfill(5),
        em_time	= None
    )

    model_phone_list.append(model_phone)

    # Phonescraper Model
    model_phonescraper = models.PhoneScraper(
        devicename = 'SEP' + str(count).zfill(12),
        sn = "FCH0FC" + str(count).zfill(5),
        firmware = 'FW Scrape' + str(count),
        dn = "31025" + str(count).zfill(5),
        model = temp_model,
        kem1 = "",
        kem2 = "",
        domain_name = "voip.customer.com",
        dhcp_server = "10.2.3.2",
        dhcp = "Yes",
        ip_address = temp_ip,
        subnetmask = "255.255.255.0",
        gateway = "10.1.1.1",
        dns1 = "10.5.5.2",
        dns2 = "10.6.5.2",
        alt_tftp = "No",
        tftp1 = "10.10.1.2",
        tftp2 = "10.20.1.2",
        op_vlan = "400",
        admin_vlan = "600",
        cucm1 = "ucm1.voip.customer.com",
        cucm2 = "ucm2.voip.customer.com",
        cucm3 = "ucm3.voip.customer.com",
        cucm4 = None,
        cucm5 = None,
        info_url = "ucm1.voip.customer.com/info/index.jsp",
        dir_url = "ucm1.voip.customer.com/directory/index.jsp",
        msg_url = None,
        svc_url = None,
        idle_url = None,
        info_url_time = None,
        proxy_url = None,
        auth_url = "ucm1.voip.customer.com/authentication/index.jsp",
        tvs = "ucm1.voip.customer.com",
        CDP_Neighbor_ID = "CDP-Host-" + str(count),
        CDP_Neighbor_IP = "CDP-IP-" + str(count),
        CDP_Neighbor_Port = "CDP-Port-" + str(count),
        LLDP_Neighbor_ID = "LLDP-ID-" + str(count),
        LLDP_Neighbor_IP = "LLDP-IP-" + str(count),
        LLDP_Neighbor_Port = "LLDP-Port-" + str(count),
        ITL = "ITL Fake Data Updated",
        date_modified = datetime.now()
    )

    model_phonescraper_list.append(model_phonescraper)

# Add Phone models list to database
crud.merge_phone_data(model_phone_list)

# Add Phonescrape model items (individual DB add due to RQ worker) to database
for item in model_phonescraper_list:
    crud.merge_phonescraper_data(item)