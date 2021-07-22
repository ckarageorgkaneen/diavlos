#!/usr/bin/env python3
from diavlos.src.site import Site
from diavlos.src.service import Service
import requests
import time
LOCALHOST = 'http://localhost:5000/v1/'
API_ENDPOINT = 'https://reg-diavlos.gov.gr/api'
NACE_API_ENDPOINT = API_ENDPOINT + '/nace/code/'

site = Site()
site.login(auto=True)

username = site._config['username']
password = site._config['password']

# SDG

query = "[[Category:Κατάλογος Διαδικασιών]][[Process nace code::+]]"
for answer in site._client.ask(query):
    page_name = answer['fulltext']
    # page_name = 'ΥΕ:Δοκιμαστική'
    page = site.pages(page_name)

    # Get service by name
    service = Service().fetch_by_name(page_name)

    newService = {'process nace': {}}

    try:
        fields = service['fields']
        naces = fields['Process nace']
        index = 1

        for nace in naces.values():
            process_nace_code = nace['process_nace_code']
            process_nace_description = nace['process_nace_description']
            index = index + 1
    except:
        r = requests.get(url=NACE_API_ENDPOINT + str(process_nace_code))
        result = r.json()['result'][0]
        description = result['description']

        newService["process nace"] = {f'{index}': {
            'process_nace_code': process_nace_code,
            'process_nace_description': description
        }}

        x = requests.put(
            LOCALHOST + 'services/name/' + str(page_name) + '/update',
            json=newService,
            auth=(username, password)
        )
        if x.status_code != 200:
            print(f'Not changed {page_name} {x.status_code}', flush=True)
        else:
            print(f'Changed {page_name} {x.status_code}', flush=True)
        time.sleep(2)
    else:
        pass
