#!/usr/bin/env python3
import argparse
import csv

from diavlos.src.site import Site
from mwtemplates import TemplateEditor
from diavlos.src.service import Service

CSV_EXTENSION = '.csv'

PUBLISHED_NAMESPACE = 'ΔΔ'
BEING_EDITTED_NAMESPACE = 'ΥΕ'
TO_BE_APPROVED_NAMESPACE = 'ΠΕ'
TO_BE_PUBLISHED_NAMESPACE = 'ΠΔ'


header_row = ['namespace', 'process_uuid', 'process_id', 'process_official_title', 'process_org_owner', 'process_source']


###
# Extract
def _service_dict(template_editor, ns=PUBLISHED_NAMESPACE):
    tpl_instances_data = {}

    for tpl_name in template_editor.templates.keys():
        tpl_instances = template_editor.templates[tpl_name]

        if tpl_name == 'Process':
            for tpl_idx, tpl_instance in enumerate(tpl_instances):
                # print(tpl_instance.name)
                tpl_instance_dict = {'namespace': ns}
                for param in tpl_instance.parameters:

                    if param.name == 'process_uuid' or \
                            param.name == 'process_id' or \
                            param.name == 'process_source' or \
                            param.name == 'process_org_owner' or \
                            param.name == 'process_official_title':
                        # print(param.name + ' ' + param.value)
                        tpl_instance_dict[param.name] = param.value

                # print(tpl_instance_dict)
                tpl_instances_data = tpl_instance_dict

    return tpl_instances_data


def main(outfile, namespace=PUBLISHED_NAMESPACE):
    if not outfile.endswith(CSV_EXTENSION):
        outfile += CSV_EXTENSION
    site = Site()
    site.login(auto=True)
    services_category = site.categories['Κατάλογος Διαδικασιών']

    with open(outfile, 'w') as f:
        csv_output = csv.DictWriter(f, fieldnames=header_row)

        csv_output.writeheader()

        for page in services_category:
            name = page.name
            split_name = name.split(':')
            ns = split_name[0]
            if ns == namespace:  # print only selected Namespace
                service_dict = _service_dict(TemplateEditor(page.text()), ns)
                # print(service_dict)
                csv_output.writerow(service_dict)

        f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outfile', help='output .csv file')
    parser.add_argument('namespace', help='namespace (ΔΔ/ΥΕ/ΠΕ/ΠΔ)')

    # print(*vars(parser.parse_args()).values())
    main(*vars(parser.parse_args()).values())
