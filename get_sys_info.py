import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Assign requests.Session instance to session variable
session = requests.Session()

# Define URL and PAYLOAD variables
URL = "https://sbx-nxos-mgmt.cisco.com/api/aaaLogin.json"
PAYLOAD = {"aaaUser": {"attributes": {"name": "admin", "pwd": "Admin_1234!"}}}

# Obtain an authentication cookie
session.post(URL, json=PAYLOAD, verify=False)

# Define SYS_URL variable
SYS_URL = "https://sbx-nxos-mgmt.cisco.com/api/mo/sys.json"

# Obtain system information by making session.get call
# then convert it to JSON format then filter to system attributes
response = session.get(SYS_URL, verify=False).json()
print(response)  # This will show you the entire JSON response

# Now, access the JSON data as you were doing before
sys_info = response["imdata"][0]["topSystem"]["attributes"]

# Print hostname, serial number, uptime and current state information
# obtained from the NXOSv9k
print("HOSTNAME:", sys_info.get("name"))
print("SERIAL NUMBER:", sys_info.get("serial"))
print("UPTIME:", sys_info.get("systemUpTime"))
print(
    "CURRENT STATE:", sys_info.get("state", "Unavailable")
)  # Provide a default value in case 'state' does not exist
