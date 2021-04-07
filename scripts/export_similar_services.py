#!/usr/bin/env python3
import argparse
import csv
from fuzzywuzzy import fuzz
from diavlos.src.site import Site
NS = '9006'  # ΥΕ
CSV_EXTENSION = '.csv'
CSV_HEADER_TITLE = 'Τίτλος'
CSV_HEADER_SIMILAR_TITLES = 'Όμοιοι Τίτλοι'
DEFAULT_SIMILARITY_PCT = 80
site = Site()
site.login(auto=True)


def write_similar_services(outfile, similarity):
    if CSV_EXTENSION not in outfile:
        outfile += CSV_EXTENSION
    print('Fetching titles...')
    titles = [page.page_title for page in site._client.allpages(namespace=NS)]
    similar_titles_dict = {}
    print('Finding similar titles for each...')
    for t1 in titles:
        for t2 in titles:
            if t1 != t2 and fuzz.partial_ratio(t1, t2) >= similarity:
                try:
                    similar_titles_dict[t1].append(t2)
                except KeyError:
                    similar_titles_dict[t1] = [t2]
    print('Writing to output file...')
    with open(outfile, 'w') as f:
        csv_output = csv.writer(f)
        csv_output.writerow([CSV_HEADER_TITLE, CSV_HEADER_SIMILAR_TITLES])
        for t, similar_titles in similar_titles_dict.items():
            csv_output.writerow([t, '\n'.join(similar_titles)])
    print('Done.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outfile', help='output .csv file')
    parser.add_argument(
        '-s', '--similarity', type=int,
        help=f'similarity percentage (default: {DEFAULT_SIMILARITY_PCT})',
        default=DEFAULT_SIMILARITY_PCT)
    write_similar_services(*vars(parser.parse_args()).values())
