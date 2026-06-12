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
        # Regex to look for standard IPv4 addresses in the output
        ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

        for line in result.stdout.splitlines():
     	    match = ip_pattern.search(line)
     	    if match:
     	        ip = match.group(0)
                            # Avoid adding the destination IP repeatedly if the trace finishes early
     	        if ip not in ips_found:
     	            ips_found.append(ip)
        return ips_found

    except FileNotFoundError:
        print("Error: 'tracepath' command not found. Ensure it is installed on your Linux system.")
        return []
def geolocate_ips(ip_list):
    print("\nGeolocating discovered IPs...")
    hop_data = []
    for ip in ip_list:
        # We cannot geolocate private local ip addresses
        if ipaddress.ip_address(ip).is_private:
            print(f"Hop IP: {ip} (Private Local Network - Skipping)")
            continue
        try:
            # using the free ip-api
            response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,isp", timeout=5)
            data = response.json()
            if data.get("status") == "success":
                hop_info = {
                    "ip": ip,
                    "isp": data.get("isp"),
                    "country": data.get("country"),
                    "region": data.get("regionName"),
                    "city": data.get("city"),
                    "postcode": data.get("zip", "No Postcode Provided") 
                }
                hop_data.append(hop_info)
                print(f"Hop IP: {ip} | Location: {hop_info['city']}, {hop_info['country']} | Postcode: {hop_info['postcode']}")
            else:
                print(f"Hop IP: {ip} | Geolocation Failed")
        except requests.exceptions.RequestException as e:
            print(f"Error querying API for {ip}: {e}")

    return hop_data

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
geolocate_ips(IPs)
