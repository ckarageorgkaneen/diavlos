#!/usr/bin/env python3
from diavlos.src.site import Site
from diavlos.src.service import Service
import requests
LOCALHOST = 'http://localhost:5000/v1/'
API_ENDPOINT = 'https://reg-diavlos.gov.gr/api'
SDG_API_ENDPOINT = API_ENDPOINT + '/sdg/code/'

site = Site()
site.login(auto=True)

username = site._config['username']
password = site._config['password']

# SDG

query = "[[Category:Κατάλογος Διαδικασιών]][[Process sdg code::+]]"
for answer in site._client.ask(query):
    page_name = answer['fulltext']
    # page_name = 'ΥΕ:Δοκιμαστική'
    page = site.pages(page_name)

    # Get service by name
    service = Service().fetch_by_name(page_name)

    newService = {'process sdg': {}}

    try:
        fields = service['fields']
        sdgs = fields['Process sdg']
        index = 1

        for sdg in sdgs.values():
            process_sdg_code = sdg['process_sdg_code']
            process_sdg_title = sdg['process_sdg_title']
            process_sdg_description = sdg['process_sdg_description']
            index = index + 1
    except:
        r = requests.get(url=SDG_API_ENDPOINT + str(process_sdg_code))
        result = r.json()['result'][0]
        title = result['title']
        description = result['description']

        newService["process sdg"] = {f'{index}': {
            'process_sdg_code': process_sdg_code,
            'process_sdg_title': title,
            'process_sdg_description': description
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
    else:
        pass
