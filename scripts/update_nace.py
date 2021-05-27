#!/usr/bin/env python3
import argparse

from diavlos.src.site import Site
from diavlos.src.service import Service
from diavlos.src.service.error import ServiceErrorCode

import requests

API_ENDPOINT = 'http://localhost:5000/v1/'
# API_ENDPOINT = 'http://api.reg-diavlos.gov.gr:5000/v1/'
DELETE_ME = 'DELETE_ME'

PROCESS_NACE_CODE_FIELD_NAME = 'process_nace_code'
PROCESS_NACE_DESCRIPTION_FIELD_NAME = 'process_nace_description'

# process_namespaces = [
#     '9002',  # ΔΔ
#     '9006',  # ΥΕ
#     '9008',  # ΠΕ
#     '9010',  # ΠΔ
# ]

site = Site()
site.login(auto=True)


class ServiceError(Exception):
    """ServiceError exception"""


def checkIfExists(name):
    service = Service().fetch_by_name(name)
    if not service or service == ServiceErrorCode.NOT_FOUND:
        print('Not found', name, flush=True)
        return None

    try:
        processFields = service['fields']
        process_nace_code = processFields['Process'][1][PROCESS_NACE_CODE_FIELD_NAME]
    except KeyError:
        print(
            'No nace_code in Process field for: ',
            service['name'],
            flush=True)
        return None

    try:
        process_nace_description = processFields['Process'][1][PROCESS_NACE_DESCRIPTION_FIELD_NAME]
    except KeyError:
        print(
            'No nace_description in Process field for: ',
            service['name'],
            flush=True)
        return None

    return service


def changeNace(name, service):
    processFields = service['fields']
    try:
        process_nace_code = processFields['Process'][1][PROCESS_NACE_CODE_FIELD_NAME]
    except KeyError:
        return KeyError

    if process_nace_code:
        try:
            process_nace_description = processFields['Process'][1][PROCESS_NACE_DESCRIPTION_FIELD_NAME]
        except KeyError:
            print(
                'No process_nace_description for',
                service['name'],
                flush=True)
            return KeyError

        # if nace_code migration exists
        try:
            newProcess_nace_code = processFields['Process_nace'][1][PROCESS_NACE_CODE_FIELD_NAME]
            newProcess_nace_description = processFields['Process_nace'][1][PROCESS_NACE_DESCRIPTION_FIELD_NAME]

            print('nace_code migration exists', flush=True)

            newService = {
                'process': {
                    "1": {
                        PROCESS_NACE_CODE_FIELD_NAME: DELETE_ME,
                        PROCESS_NACE_DESCRIPTION_FIELD_NAME: DELETE_ME}}}

        except KeyError:
            newService = {
                'process': {
                    "1": {
                        PROCESS_NACE_CODE_FIELD_NAME: DELETE_ME,
                        PROCESS_NACE_DESCRIPTION_FIELD_NAME: DELETE_ME}},
                'process_nace': {
                    "1": {
                        PROCESS_NACE_CODE_FIELD_NAME: process_nace_code,
                        PROCESS_NACE_DESCRIPTION_FIELD_NAME: process_nace_description}}}

        x = requests.put(
            API_ENDPOINT +
            'services/name/' +
            str(name) +
            '/update',
            json=newService,
            auth=(
                'Master',
                '1T*X8@kix7sm'))
        # print(x)

        if x.status_code != 200:
            print('Not Changed ', flush=True)

        serviceName = name  # get page name
        page = site.pages(f'{serviceName}')  # get page
        text = page.text()

        row = "|" + PROCESS_NACE_CODE_FIELD_NAME + "=" + "DELETE_ME" + '\n'

        if text.find(row) != -1:
            page.edit(page.text().replace(
                row, ""
            ))

        row = "|" + PROCESS_NACE_DESCRIPTION_FIELD_NAME + "=" + "DELETE_ME" + '\n'
        if text.find(row) != -1:
            page.edit(page.text().replace(
                row, ""
            ))

        print(f'Changed {serviceName} {x.status_code}', flush=True)


def main(name):
    site.login(auto=True)

    if name == "all":
        # for ns in process_namespaces:
        #     print('Namespace: ', ns, flush=True)
        # for page in site._client.allpages(namespace=ns):
        pages = site.categories['Κατάλογος Διαδικασιών']
        for count, page in enumerate(pages):
            name = page.name
            id_ = Service().get_id_by_fullname(name)
            service = checkIfExists(name)
            if service:
                print(name, flush=True)
                changeNace(name, service)

    else:
        service = checkIfExists(name)
        if service:
            changeNace(name, service)

    print('Finished', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pid', help='id of process or "all"')
    main(*vars(parser.parse_args()).values())

# changeNace(754738)
# deleteFields(754738)
