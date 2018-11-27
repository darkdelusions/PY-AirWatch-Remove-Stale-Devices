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


def find_offline():
    #Sets the number of days offline from config file
    days_offline = int(config['general']['days_offline'])
    #Tests to ensure days offline is set
    if days_offline:
        #Subtracts X days from Today to determine the date airwatch should pull from
        unformatted_date = datetime.today() - timedelta(days=70)
        #Converts Date and Time format to MM/DD/YYYY
        offline_since = unformatted_date.strftime("%m" + "/" + "%d" + "/" + "%Y")
        #Sets Up Query
        formatted_url = url + "/API/mdm/devices/search"
        query_string = {"lastseen":offline_since}
        #API Call
        try:
            print("Connecting to: " + url)
            print("Looking for Devices that have been offline since " + offline_since)
            response = requests.get(formatted_url, headers=headers, params=query_string).json()
            output = { 'BulkValues':{'Value':[item['SerialNumber'] for item in response['Devices']]}}
            return(output)
        except json.decoder.JSONDecodeError:
            sys.exit("No devices found offline for " + str(days_offline) + "+ days")

    else:
            sys.exit("URL or Days_Offline are not set in the Config")

def delete_devices():
    formatted_url = url + "/API/mdm/devices"
    input = find_offline()
    #response = requests.post(formatted_url, headers=headers, json=input)
    print(input)
    sys.exit('Device deletion completed.')
delete_devices()
