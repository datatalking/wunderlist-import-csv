import configparser
import requests
import csv
import json

config = configparser.ConfigParser()
config.read('app.ini')

wl = config['wunderlist']

def fetch_from_api(fetch_url):
    url = wl['api_base'] + fetch_url
    headers = {'X-Access-Token': wl['access_token'], 'X-Client-ID': wl['client_id']}
    response = requests.get(url, headers=headers)
    return response.json()


def push_to_api(push_url, payload, patch=False):
    url = wl['api_base'] + push_url
    headers = {'X-Access-Token': wl['access_token'], 'X-Client-ID': wl['client_id'], 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Load Lists, make dict of name -> ID
all_lists = fetch_from_api('/lists')
lists = { list['title']: list['id'] for list in all_lists }

# For each record in CSV
csv_file_name = config['main']['csv_file']
with open(csv_file_name) as csv_file:
    for row in csv.DictReader(csv_file):
        list_name = row['List']
        list_id = lists[list_name]
        if not list_id:
            raise 'Invalid list: {0}'.format(list_name)
        task_title = row['Task']
        note = row['Note']
        if row['Additional Note']:
            note = note + '\n\n' + row['Additional Note']

        # Push new task
        print('Creating task "{0}" in list "{1}"'.format(task_title, list_name))
        new_task = push_to_api('/tasks', { 'list_id': list_id, 'title': task_title })
        # Retrieve ID of new task
        new_task_id = new_task['id']
        # Push note of new task
        print('Adding note to new task {0}'.format(new_task_id))
        push_to_api('/notes', { 'task_id': new_task_id, 'content': note})
