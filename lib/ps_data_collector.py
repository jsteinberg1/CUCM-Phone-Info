import os
import requests
import time

current_time = time.strftime("%Y%m%d-%H%M%S")

headers = {}
requests_time = 3


print("*****Phone Scraper Data Collector Tool*****")
print("This utility supports multiple URLs.  When you are finished supplying URLs press enter on a blank line.\n\n")
phone_model = input("Enter phone model (e.g. 8841): ")

file_name = f"{phone_model}-{current_time}.txt"

f = open(file_name, "a")
f.write(f"Collecting data for phone model {phone_model}\n")

while True:
    url_to_scrape = input("Enter full URL to scrape (e.g. http://10.1.40.12/CGI/Java/Serviceability?adapter=device.statistics.configuration ): ")

    if url_to_scrape == "":
        break

    f.write("***********************************************************************************\n")
    f.write(f"connecting to {url_to_scrape}\n")
    f.write("***********************************************************************************\n")

    try:
        config_response = requests.request("GET", url_to_scrape, headers=headers, timeout=requests_time)
        f.write(config_response.text + "\n")
        f.write("***********************************************************************************\n")
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(f"unable to connect {e} - {url_to_scrape}")
        f.write(f"unable to connect to {url_to_scrape}\n")

print(f"Data saved to log file {file_name}")
f.close()