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
# I need to check whether the % of latest busy% value is less than 5. If it is then 
#the program continues if not then the program keeps waiting







#def get_busy_percentage():
#   perc_cpu = os.system('sudo turbostat -q -S --show Busy% -i 1')
#   lines = perc_cpu.stdout.strip().split('\n')
#   print(lines)

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
#   cmd = ['python3','matmul_fast.py']
#   run = subprocess.run(cmd,capture_output=True,text=True,check=True)

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

def get_carbon_intensity():
   #Define NESO API endpoint URL
   url= 'https://api.carbonintensity.org.uk/intensity'
   header= {'Accept:','application/json'}

   try:
   	#Make a GET request to the API
   	response = requests.get(url)

   	if response is not None:
   	   data = response.json()
   	   #print(data)
   	   current_intensity = data['data'][0]['intensity']['actual']
   	   return current_intensity
   	else:
   	   print("Invalid Response from NESO API")

   except subprocess.CalledProcessError as e:
   	print("failed to get Energy data")
   	print(f"Error details: {e.stderr}")


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

CI = get_carbon_intensity()
print(f"The Carbon intensity in the Uk is {CI} gCO2/kWh")
