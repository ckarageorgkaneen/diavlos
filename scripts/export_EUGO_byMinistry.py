#!/usr/bin/env python3
import argparse
import csv

from diavlos.src.site import Site
from mwtemplates import TemplateEditor
from diavlos.src.service import Service
from diavlos.src.service.error import ServiceErrorCode

CSV_EXTENSION = '.csv'

PUBLISHED_NAMESPACE = 'ΔΔ'
BEING_EDITTED_NAMESPACE = 'ΥΕ'
TO_BE_APPROVED_NAMESPACE = 'ΠΕ'
TO_BE_PUBLISHED_NAMESPACE = 'ΠΔ'


header_row = [
    'name',
    'Υπουργείο',
]

def checkIfExists(name):
    service = Service().fetch_by_name(name)
    if not service or service == ServiceErrorCode.NOT_FOUND:
        return None

    return service

def main(outfile):
    if not outfile.endswith(CSV_EXTENSION):
        outfile += CSV_EXTENSION
    site = Site()
    site.login(auto=True)
    services_category = site.categories['Κατάλογος Διαδικασιών']

    with open(outfile, 'w') as f:
        csv_output = csv.DictWriter(f, fieldnames=header_row)
        for page in services_category:
            service = checkIfExists(page.name)
            if service:
                try:

                    process_source = service['fields']['Process'][1]['process_source']
                    if process_source == "EU-GO":
                        print(page.name)
                        process_org_owner = service['fields']['Process'][1]['process_org_owner']
                        csv_output.writerow({
                            'name': page.name,
                            'Υπουργείο': process_org_owner
                        })
                except KeyError:
                    pass
        print('Finished')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outfile', help='output .csv file')

    main(*vars(parser.parse_args()).values())
