#!/usr/bin/env python3
import argparse
import csv
import re
import xmltodict
from diavlos.src.site import Site
CSV_EXTENSION = '.csv'
PAGE_SCHEMA_KEY = 'PageSchema'
TEMPLATE_KEY = 'Template'
TAG_NAME_KEY = '@name'
TAG_MULTIPLE_KEY = '@multiple'
PAGEFORMS_TEMPLATE_DETAILS_KEY = 'pageforms_TemplateDetails'
FIELD_KEY = 'Field'
LABEL_KEY = 'Label'
PAGEFORMS_FORM_INPUT_KEY = 'pageforms_FormInput'
INPUT_TYPE_KEY = 'InputType'
PARAMETER_KEY = 'Parameter'
SMW_PROPERTY_KEY = 'semanticmediawiki_Property'
TYPE_KEY = 'Type'
ALLOWED_VALUE_KEY = 'AllowedValue'
PAGE_SCHEMAS_CSV_HEADER_MAP = {
    TEMPLATE_KEY: {
        TAG_NAME_KEY: TEMPLATE_KEY,
        TAG_MULTIPLE_KEY: f'Repeater {TEMPLATE_KEY}?',
        PAGEFORMS_TEMPLATE_DETAILS_KEY: {
            LABEL_KEY: f'{LABEL_KEY} ({TEMPLATE_KEY})',
        }
    },
    FIELD_KEY: {
        TAG_NAME_KEY: FIELD_KEY,
        LABEL_KEY: f'{LABEL_KEY} ({FIELD_KEY})',
        PAGEFORMS_FORM_INPUT_KEY: {
            INPUT_TYPE_KEY: 'PageForms Input Type',
            PARAMETER_KEY: {
                TAG_NAME_KEY: f'Has Mandatory Parameter?'
            }
        },
        SMW_PROPERTY_KEY: {
            TYPE_KEY: 'SMW Property Type',
            ALLOWED_VALUE_KEY: 'Allowed Values'
        },

    }
}


def value_from_nested_dict(dict_, *nested_keys):
    val = dict_
    for k in nested_keys:
        if not isinstance(val, dict):
            return val
        val = val.get(k)
    return val


def get_template_row(template_dict):
    row = [
        value_from_nested_dict(template_dict, TAG_NAME_KEY),
        value_from_nested_dict(template_dict, TAG_MULTIPLE_KEY) is not None,
        value_from_nested_dict(
            template_dict, PAGEFORMS_TEMPLATE_DETAILS_KEY, LABEL_KEY)
    ]
    return row


def get_field_row(field_dict):
    row = [
        value_from_nested_dict(field_dict, TAG_NAME_KEY),
        value_from_nested_dict(field_dict, LABEL_KEY),
        value_from_nested_dict(
            field_dict, PAGEFORMS_FORM_INPUT_KEY, INPUT_TYPE_KEY),
        value_from_nested_dict(
            field_dict, PAGEFORMS_FORM_INPUT_KEY, PARAMETER_KEY,
            TAG_NAME_KEY) is not None,
        value_from_nested_dict(
            field_dict, SMW_PROPERTY_KEY, TYPE_KEY),
        value_from_nested_dict(
            field_dict, SMW_PROPERTY_KEY, ALLOWED_VALUE_KEY),
    ]
    return row


def create_header_row():
    # Header strings
    template = PAGE_SCHEMAS_CSV_HEADER_MAP[TEMPLATE_KEY][TAG_NAME_KEY]
    template_repeater = PAGE_SCHEMAS_CSV_HEADER_MAP[TEMPLATE_KEY][
        TAG_MULTIPLE_KEY]
    template_label = PAGE_SCHEMAS_CSV_HEADER_MAP[TEMPLATE_KEY][
        PAGEFORMS_TEMPLATE_DETAILS_KEY][LABEL_KEY]
    field = PAGE_SCHEMAS_CSV_HEADER_MAP[FIELD_KEY][TAG_NAME_KEY]
    field_label = PAGE_SCHEMAS_CSV_HEADER_MAP[FIELD_KEY][LABEL_KEY]
    field_pageforms_form_input_type = PAGE_SCHEMAS_CSV_HEADER_MAP[
        FIELD_KEY][PAGEFORMS_FORM_INPUT_KEY][INPUT_TYPE_KEY]
    field_mandatory = PAGE_SCHEMAS_CSV_HEADER_MAP[FIELD_KEY][
        PAGEFORMS_FORM_INPUT_KEY][PARAMETER_KEY][TAG_NAME_KEY]
    field_smw_property_type = PAGE_SCHEMAS_CSV_HEADER_MAP[FIELD_KEY][
        SMW_PROPERTY_KEY][TYPE_KEY]
    field_smw_allowed_values = PAGE_SCHEMAS_CSV_HEADER_MAP[
        FIELD_KEY][SMW_PROPERTY_KEY][ALLOWED_VALUE_KEY]
    header_row = [
        template,
        template_repeater,
        template_label,
        field,
        field_label,
        field_pageforms_form_input_type,
        field_mandatory,
        field_smw_property_type,
        field_smw_allowed_values,
    ]
    return header_row


def main(outfile):
    if not outfile.endswith(CSV_EXTENSION):
        outfile += CSV_EXTENSION
    site = Site()
    site.auto_login()
    services_category = site.categories['Κατάλογος Διαδικασιών']
    services_category_text = services_category.text()
    services_page_schema_xml = re.sub(
        r'{{.*}}', '', services_category_text, flags=re.S)
    services_page_schema = xmltodict.parse(services_page_schema_xml)
    # import json
    # print(json.dumps(services_page_schema, indent=4, ensure_ascii=False))
    with open(outfile, 'w') as f:
        csv_output = csv.writer(f)
        header_row = create_header_row()
        header_row_length = len(header_row)
        csv_output.writerow(header_row)
        templates = services_page_schema[PAGE_SCHEMA_KEY][TEMPLATE_KEY]
        for template in templates:
            for field in template[FIELD_KEY]:
                row = get_template_row(template)
                field_row = get_field_row(field)
                row.extend(field_row)
                row_length = len(row)
                assert row_length == header_row_length
                csv_output.writerow(row)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outfile', help='output .csv file')
    main(*vars(parser.parse_args()).values())
