import requests
import re
import bz2
import json
import csv


def get_list_of_sde_versions():
    list_url = "https://www.fuzzwork.co.uk/dump/"
    RE_SDE = re.compile(r'sde-\d{8}-TRANQUILITY\/')

    text = requests.get(list_url).text
    result = re.findall(RE_SDE, text)
    return set(result)


def get_current_types():
    """
    Returns JSON object representing the current SDE from zzeve.
    """
    url = "http://sde.zzeve.com/invTypes.json"

    json = requests.get(url).json()
    return json


def start():
    print("Getting current ESI...\n")
    current = get_current_types()

    print("Getting list of SDE versions...")
    versions = get_list_of_sde_versions()

    base_url = "https://www.fuzzwork.co.uk/dump/"
    file_name = "invTypes.csv.bz2"

    print("Processing versions...")
    save_data = set(('name', 'typeID'))
    for version in versions:
        print(f"Processing {version[:-1]}...")
        comp_dict = {}
        try:
            print("Getting data...")
            data = requests.get(base_url + version + file_name)
            # Get the bz2 file
            with open(file_name, 'wb') as dataFile:
                dataFile.write(data.content)
            
            # Extract the bz2 file to something we can read.
            with open('invTypes.csv', 'wb') as dataFile:
                dataFile.write(bz2.open(file_name, 'rb').read())

            print("Reading data...")
            with open('invTypes.csv', 'r', encoding='utf8') as csvFile:
                reader = csv.DictReader(csvFile)
                for row in reader:
                    comp_dict[int(row['typeID'])] = row['typeName']

            for item in current:
                if item['typeID'] in comp_dict and comp_dict[item['typeID']] != item['typeName']:
                    save_data.add((comp_dict[item['typeID']], item['typeID']))

        except Exception as e:
            print(f"Oops, something went wrong with {version}!")
            print(e)
            print("Continuing!")
            continue
        finally:
            del comp_dict, data

    # Remove empty names
    for item in save_data.copy():
        if item[0] is '':
            save_data.remove(item)

    print("Writing CSV file.")
    with open('typeNameChanges.csv', 'w', newline='', encoding='utf8') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(save_data)


if __name__ == '__main__':
    start()