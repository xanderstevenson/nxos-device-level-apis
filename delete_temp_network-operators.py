import requests
import json

# Suppress only the single InsecureRequestWarning from urllib3 needed
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Define the URL and headers for NX-API
url = 'https://sbx-nxos-mgmt.cisco.com/ins'
headers = {'content-type': 'application/json-rpc'}

# NX-API credentials
username = 'admin'
password = 'Admin_1234!'

# Create a session for persistent connections
session = requests.Session()
session.auth = (username, password)

# Payload to retrieve all users
payload = {
    "jsonrpc": "2.0",
    "method": "cli",
    "params": {
        "cmd": "show user-account",
        "version": 1
    },
    "id": 1
}

# Send the request to get all user accounts
response = session.post(url, json=payload, headers=headers, verify=False)

# Function to delete a user and save the configuration
def delete_user(user):
    # Command to delete user and save the configuration
    delete_commands = [
        "configure terminal",
        "no username {user}".format(user=user),
        "end",
        "copy running-config startup-config"
    ]
    
    # Send each command to the device
    for cmd in delete_commands:
        delete_payload = {
            "jsonrpc": "2.0",
            "method": "cli",
            "params": {
                "cmd": cmd,
                "version": 1
            },
            "id": 1
        }
        delete_response = session.post(url, json=delete_payload, headers=headers, verify=False)
        
        # Check the response for each command
        if delete_response.status_code == 200:
            print("Command '{}' executed successfully.".format(cmd))
        else:
            print("Failed to execute command '{}'. Status code: {}, Response: {}".format(cmd, delete_response.status_code, delete_response.text))
            break  # Stop executing further commands if one fails

# Check if the response was successful
if response.status_code == 200:
    users = response.json()

    try:
        # Extract the list of users from the response
        user_entries = users['result']['body']['TABLE_template']['ROW_template']
        
        # Initialize an empty list to store specific usernames
        temp_network_operator_users = []
        
        # Normalize single user entry to a list
        if isinstance(user_entries, dict):
            user_entries = [user_entries]

        # Iterate over the user entries
        for user_entry in user_entries:
            username = user_entry['usr_name']
            role_data = user_entry.get('TABLE_role', {}).get('ROW_role', {})
            # Normalize single role entry to a list
            if isinstance(role_data, dict):
                role_data = [role_data]

            roles = [role_entry['role'] for role_entry in role_data if 'role' in role_entry]
            
            # If 'network-operator' is in the roles and 'temp' in the username, add to the list
            if 'network-operator' in roles and 'temp' in username.lower():
                temp_network_operator_users.append(username)
        
        # Output the users that match the criteria
        print("Users to be deleted: {}".format(temp_network_operator_users))
        
        # Proceed to delete the users
        for user in temp_network_operator_users:
            delete_user(user)  # Call the function to delete each user

    except KeyError as e:
        print("KeyError: {} - The expected key is not in the JSON response.".format(e))
else:
    print("Failed to retrieve users. Status code: {}, Response: {}".format(response.status_code, response.text))

# Close the session
session.close()
