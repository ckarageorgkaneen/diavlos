#!/usr/bin/env python3
import re
import requests
import argparse
from diavlos.src.site import Site

SERVICES_ENDPOINT = 'https://www.gov.gr/api/v1/services/?format=json'


def main(delete=False):
    r = requests.get(SERVICES_ENDPOINT)
    r.raise_for_status()
    govgr_services = r.json()
    govgr_services_titles = [re.sub(' +', ' ', d['title'])
                             for d in govgr_services]
    site = Site()
    site.login(auto=True)
    # for title in govgr_services_titles:
    #     print(title)
    if delete:
        print('Διαδικασίες που διαγράφτηκαν,ID')
    else:
        print('Διαδικασίες προς-διαγραφή (δεν υπάρχουν πια στο gov.gr),ID')
    for page in site.categories['Κατάλογος Διαδικασιών']:
        if 'process_source=gov.gr' in page.text():
            page_title = page.page_title
            if page_title not in govgr_services_titles:
                if delete:
                    page.delete(reason='Παλιά διαδικασία gov.gr')
                print(f'"{page_title}",{page.pageid}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Delete old gov.gr services.'
        'Perform a dry run, unless the delete argument is given.')
    parser.add_argument('--delete', action='store_true',
                        help='do the actual deletion')
    main(**vars(parser.parse_args()))
