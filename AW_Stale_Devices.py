import requests, os, configparser, csv, sys, json
from datetime import datetime, timedelta

#Config File Setup

config = configparser.ConfigParser()
config.read('config.ini')

##Creates header based off the config file
if config['general']['default_instance'] == "prod":
    url = config['instance']['prod']
    headers = {
        'aw-tenant-code': config['prod']['aw-tenant-code'],
        'content-type': 'application/json',
        'authorization': "Basic " + config['prod']['authorization'],
        'cache-control': 'no-cache'
    }
elif config['general']['default_instance'] == "qat":
    url = config['instance']['qat']
    headers = {
        'aw-tenant-code': config['qat']['aw-tenant-code'],
        'content-type': 'application/json',
        'authorization': "Basic " +  config['qat']['authorization'],
        'cache-control': 'no-cache'
    }
elif config['general']['default_instance'] == "test":
    url = config['instance']['test']
    headers = {
        'aw-tenant-code': config['test']['aw-tenant-code'],
        'content-type': 'application/json',
        'authorization': "Basic " +  config['test']['authorization'],
        'cache-control': 'no-cache'
    }

else:
    sys.exit("No Server is defined in the config file")


def main():
    payload = find_offline()
    script_mode = config['general']['script_mode']
    count = len(payload['BulkValues']['Value'])
    max_number = config['general']['max_number_devices_warning']
    if count > 0:
        if script_mode == "auto":
            print("Script Running in Auto Mode")
            print("If you would like to change this please change the script_mode to manual in the config.ini")
            print("Deleting" + str(count) + "devices")
            write_csv(payload)
            json_payload = json.dumps(payload)
            print("test")
            delete_devices(json_payload)
        elif script_mode == "manual":
            user_input = ''
            while user_input != 'n':
                print(f"You are about to delete {str(count)} devices")
                user_input = input("Do you want to continue? [y/n]: ")
                if user_input == "y":
                    print("Starting Devices Deletions")
                    write_csv(payload)
                    json_payload = json.dumps(payload)
                    delete_devices(json_payload)
                elif user_input == "n":
                    sys.exit("Script Aborted")
                else:
                    print("")
                    print("Invaild selection please use [y/n].")
                    print("")
        else:
            sys.exit("Please Set the script_mode in the config.ini")
    else:
        sys.exit("There is nothing to Delete")

def days_offline():
    #Sets the number of days offline from config file
    days_offline = int(config['general']['days_offline'])
    #Tests to ensure days offline is set
    if days_offline:
        #Subtracts X days from Today to determine the date airwatch should pull from
        unformatted_date = datetime.today() - timedelta(days=days_offline)
        #Converts Date and Time format to MM/DD/YYYY
        offline_since = unformatted_date.strftime("%m" + "/" + "%d" + "/" + "%Y")
        return(offline_since)
    else:
        sys.exit("URL or Days_Offline are not set in the Config")

def write_csv(payload):
    offline_since = days_offline()
    if os.path.exists("offlinedevices.csv"):
        with open('offlinedevices.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            for device in payload['BulkValues']['Value']:
                writer.writerow([device, offline_since, datetime.today()])
    else:
        with open('offlinedevices.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Serial Number','Days Since', 'Deleted On'])
            for device in payload['BulkValues']['Value']:
                print(device)
                writer.writerow([device, offline_since, datetime.today()])


def find_offline():
    offline_since = days_offline()
    dayz_offline = int(config['general']['days_offline'])
    endpoint_url = url + "/API/mdm/devices/search"
    #Sets the Query Paramters
    query_string = {"lastseen":offline_since}
    #API Call
    try:
        print(f"Connecting to: {url}")
        print(f"Looking for Devices that have been offline since {offline_since}")
        response = requests.get(endpoint_url, headers=headers, params=query_string).json()
        output = {"BulkValues":{"Value":[item['SerialNumber'] for item in response['Devices']]}}
        return(output)
    except json.decoder.JSONDecodeError:
        sys.exit(f"No devices found offline for {str(dayz_offline)}+ days")



def delete_devices(json_payload):
    #Formats URL for Query
    endpoint_url = url + "/API/mdm/devices/bulk"
    #Creates the JSON payload to be sent to the server
    #API Call
    query_string = {"searchBy":"SerialNumber"}
    response = requests.post(endpoint_url, params=query_string, data=json_payload, headers=headers).json()
    print(response)
    sys.exit('Device deletion completed.')
main()
