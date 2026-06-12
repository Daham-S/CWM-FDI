# Wait until cpu is at Idle using turbostat
# Run a computationally intensive task - could be matmul_slow/fast
# Use TurboStat to check the energy consumption of the task
# Use the NESO API to check the Carbon Intensity of wherever the program was run from
# Using the Energy and CI to calc the carbon footprint
# be able to select a secondary region
# check the carbon footprint of sending and running the program to a 
#theoretical identical machine in that region
# Maybe the Program could later list the different regions where it would be 
#cheaper to send and run the program

import os
import time
import subprocess
import requests
import re
import ipaddress
# I need to check whether the % of latest busy% value is less than 5. If it is then 
#the program continues if not then the program keeps waiting







#def get_busy_percentage():
#     perc_cpu = os.system('sudo turbostat -q -S --show Busy% -i 1')
#     lines = perc_cpu.stdout.strip().split('\n')
#     print(lines)

# find busy percentage



def get_busy_percentage():
     #pass command as a list of arguments
     cmd = ['sudo','turbostat','-q','-S','--show','Busy%', '-i', '1','-n', '1']
     try:
     	perc_cpu = subprocess.run(cmd, capture_output=True, text=True, check=True)
     	lines = perc_cpu.stdout.strip().splitlines()
     	busy_perc = float(lines[1])

     except:
     	print("failed to get CPU data")
     # Check if the 
     return busy_perc

#get_busy_percentage()

#busy = True


# run matmul_fast.py 

#def run_program():
#     cmd = ['python3','matmul_fast.py']
#     run = subprocess.run(cmd,capture_output=True,text=True,check=True)

def check_energy_usage():
     cmd = ['sudo','turbostat','-q','--Joules','--show','Pkg_J', 'python3', 'matmul_fast_modified.py','500']
     try:
     	result = subprocess.run(cmd, capture_output=True, text=True, check=True)
     	raw_output = result.stderr.strip()
     	lines = raw_output.splitlines()
     	energy_joules = None
     	for i, line in enumerate(lines):
     	     if line == 'Pkg_J':
     	     	#Grab the next line 
     	     	energy_joules = float(lines[i+1])
     	     	break
     	if energy_joules is not None:
     	     return energy_joules
     	else:
     	     print("failed to get the energy")
#  return energy_joules
     except subprocess.CalledProcessError as e:
     	print("failed to get Energy data")
     	print(f"Error details: {e.stderr}")

def get_carbon_intensity(Address):
     #Define NESO API endpoint URL
     url= 'https://api.carbonintensity.org.uk/regional/postcode/' + Address
     header= {'Accept':'application/json'}

     try:
     	#Make a GET request to the API
     	response = requests.get(url, headers=header)

     	if response is not None:
     	     data = response.json()
#     	     print(data)
     	     regional_data = data['data'][0]
     	     current_intensity = regional_data['data'][0]['intensity']['forecast']
     	     return current_intensity
     	else:
     	     print("Invalid Response from NESO API")

     except requests.exceptions.RequestException as e:
     	print("failed to get Energy data due to network error")
     	print(f"Error details: {e}")

def local_carbon_footprint(energy_usage, carbon_intensity):
     energy = energy_usage / (3.6 * 10**6)
     carbon_footprint = energy * carbon_intensity
     return carbon_footprint



#Find the path of the data using trace route getting the IP addresses of the routers that our packet passes through
#Using these IP addresses Geolocate the position of the routers
#With the addresses of these routers I can calculate the carbon intensity at each of the router locations
#Assuming a constant energy usage at each of these stops we can then calc a carbon footprint
#Separate the loss of routers with endpoint devices as the loss from the NIC card on the sending and receiving devices will be #different to losses at switching routers
def discover_path(destination,max_hops=30):
    print(f"Tracing path to {destination}:")
    ips_found = []
    try:
        result = subprocess.run(
                     ['tracepath', '-n', '-m', str(max_hops), destination],
                      capture_output=True,
                      text=True,
                      check=True
             )
        data = result.stdout.splitlines()
        # use regex to look for ip address pattern
        ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

        for line in result.stdout.splitlines():
     	    match = ip_pattern.search(line)
     	    if match:
     	        ip = match.group(0)
          # stop duplicate ip addresses from being added
     	        if ip not in ips_found:
     	            ips_found.append(ip)
        return ips_found

    except:
        print("Error: failed to trace packets")
        return []

JANET_POSTCODES = {
    "aberew": "AB24",  # Elphinstone West, University of Aberdeen
    "aber": "AB24",    
    "glasss": "G3",    # South Street Node, Glasgow
    "glas": "G3",      
    "edis": "EH8",     # Edinburgh University / City Node
    "edin": "EH8",     
    "dund": "DD1",     # Dundee Node
    "manckh": "M13",   # Kilburn House, University of Manchester
    "manc": "M13",     
    "leed": "LS2",     # Leeds Regional Node
    "birm": "B15",     # Birmingham Regional Node
    "londpg": "E14",   # Powergate Data Centre / Telehouse West, London
    "erdiss": "E14",   # London Core Infrastructure Hub
    "harwat": "OX11",  # Jisc HQ, Harwell Oxford Campus
    "bris": "BS8",     # Bristol Regional Node
    "belf": "BT7"      # Belfast Node (Queen's University area)
}

def parse_janet_domain(domain_name):
    domain = domain_name.lower().strip()
    if not domain.endswith(".ja.net"):
        return None
    for substring, postcode in JANET_POSTCODES.items():
        if substring in domain:
            return postcode


def geolocate_ips(ip_list):
    print("\nGeolocating IPs")
    hop_data = []
    hop_postcodes = []
    for ip in ip_list:
        # We cannot geolocate private local ip addresses
        if ipaddress.ip_address(ip).is_private:
            print(f"Hop IP: {ip} (Private Network - Skipping)")
            continue
        try:
            # using the ip-api API
            response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,isp,reverse", timeout=5)
            data = response.json()
            if data.get("status") == "success":
                hop_info = {
                    "ip": ip,
                    "isp": data.get("isp"),
                    "country": data.get("country"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                    "postcode": data.get("zip"), 
                    "domain_name":data.get("reverse")
                }
                hop_data.append(hop_info)
                print(f"Hop IP: {ip} | Location: {hop_info['city']}, {hop_info['country']} | Postcode: {hop_info['postcode']} | Domain Name: {hop_info['domain_name']}" )
                postcode = parse_janet_domain(hop_info['domain_name'])
                hop_postcodes.append(postcode)
                print(f"Hop Postcode: {hop_postcodes}")
            else:
                print(f"Hop IP: {ip} | Geolocation Failed")
        except Exception as e:
            print(f"Error processing {ip}: {e}")

    return hop_postcodes

def get_carbon_intensity_array(hop_postcodes):

    carbon_intensities = []
    for i,postcode in enumerate(hop_postcodes):
        if postcode is None:
            continue
         #Define NESO API endpoint URL
        url= 'https://api.carbonintensity.org.uk/regional/postcode/' + postcode
        header= {'Accept':'application/json'}

        try:
            #Make a GET request to the API
            response = requests.get(url, headers=header)

            if response is not None:
                data = response.json()
#               print(data)
                regional_data = data['data'][0]
                current_intensity = regional_data['data'][0]['intensity']['forecast']
                carbon_intensities.append(current_intensity)
            else:
                print("Invalid Response from NESO API")
  
        except requests.exceptions.RequestException as e:
            print("failed to get Energy data due to network error")
            print(f"Error details: {e}")
    return carbon_intensities

def get_carbon_footprint_network(carbon_intensities,file_size):
    energy_total = 0
    #Juniper PTX10008
    router_link_capacity = 100*10**9
    router_idle_power = 12000
    router_max_power = 17300
    ports = 288
    dynamic_power = (router_max_power - router_idle_power)
    dynamic_power_per_port = dynamic_power_per_port/ports
    time = file_size/router_link_capacity
    energy_per_hop = dynamic_power_per_port*time

    for i,CI in enumerate(carbon_intensities):
        carbon_footprint_total += energy_per_hop * CI

busy = True

print("Monitoring CPU usage. Waiting for CPU usage to drop below 5%")
while busy == True:
     busy_perc = get_busy_percentage()
     print(f"Current CPU usage is {busy_perc}%")
     if busy_perc <= 5:
             busy = False
print ("succeeded")

energy_joules = check_energy_usage()
print(f"Measure of energy is {energy_joules}J")

oxf_address = 'OX1'
oxf_CI = get_carbon_intensity(oxf_address)
print(f"The Carbon intensity in Oxford is {oxf_CI} gCO2/kWh")

carbon_footprint = local_carbon_footprint(energy_joules,oxf_CI)
print(f"The Carbon footprint of running the program in Oxford is {carbon_footprint:.3g} gCO2/kWh")


aberdeen_address = 'AB24'
aberdeen_CI = get_carbon_intensity(aberdeen_address)
print(f"The Carbon intensity in Aberdeen is {aberdeen_CI} gCO2/kWh")

aberdeen_destination_ip = '139.133.246.148'
IPs = discover_path(aberdeen_destination_ip)
print(IPs)
router_postcodes = geolocate_ips(IPs)
router_carbon_intensities = get_carbon_intensity_array(router_postcodes)
print(f"The carbon intensities of the router locations are {router_carbon_intensities}")

file_size = 3.6 * 1000 * 8 
network_carbon_footprint=get_carbon_footprint_network(router_carbon_intensities,file_size)
print(f"The network carbon footprint of sending the file over the network {network_carbon_footprint}")
