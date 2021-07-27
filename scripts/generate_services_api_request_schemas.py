#!/usr/bin/env python3
import re
import yaml
from copy import deepcopy
import xmltodict
from diavlos.src.site import Site
TEXT_STR = 'text'
DROPDOWN_STR = 'dropdown'
TOKENS_STR = 'tokens'
PAGE_SCHEMA_KEY = 'PageSchema'
TEMPLATE_KEY = 'Template'
TAG_NAME_KEY = '@name'
FIELD_KEY = 'Field'
PAGEFORMS_FORM_INPUT_KEY = 'pageforms_FormInput'
INPUT_TYPE_KEY = 'InputType'
SMW_PROPERTY_KEY = 'semanticmediawiki_Property'
TYPE_KEY = 'Type'
ALLOWED_VALUE_KEY = 'AllowedValue'
JSON_SCHEMA_STR_TYPE = {'type': 'string'}
JSON_SCHEMA_ARRAY_TYPE = {
    'type': 'array',
    'items': None
}
JSON_SCHEMA_ENUM_TYPE = deepcopy(JSON_SCHEMA_STR_TYPE)
JSON_SCHEMA_ENUM_TYPE['enum'] = []
JSON_SCHEMA_OBJECT_TYPE = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {}
}
JSON_SCHEMA_UPDATE_PROPERTY_TYPE = {
    "type": "object",
    "description": ("Ένα λεξικό προτύπων, όπου τα κλειδιά είναι ο αριθμός του \
προτύπου που θέλουμε να ενημερωθεί π.χ. το κλειδί '2' σημαίνει \
το 2ο κατά σειρά πρότυπο της διαδικασίας. Αν το πρότυπο αυτό δεν \
υπάρχει, τότε προστίθεται σαν καινούριο."),
    "additionalProperties": JSON_SCHEMA_OBJECT_TYPE
}
JSON_SCHEMA_UPDATE_OBJECT_TYPE = JSON_SCHEMA_OBJECT_TYPE
site = Site()
site.login(auto=True)
service_add_schema = deepcopy(JSON_SCHEMA_OBJECT_TYPE)
service_update_schema = deepcopy(JSON_SCHEMA_OBJECT_TYPE)
services_category = site.categories['Κατάλογος Διαδικασιών']
services_category_text = services_category.text()
services_page_schema_xml = re.sub(
    r'{{.*}}', '', services_category_text, flags=re.S)
services_page_schema = xmltodict.parse(services_page_schema_xml)
templates = services_page_schema[PAGE_SCHEMA_KEY][TEMPLATE_KEY]
for template in templates:
    template_name = template[TAG_NAME_KEY]
    add_schema_array_obj = deepcopy(JSON_SCHEMA_ARRAY_TYPE)
    add_schema_array_obj['items'] = deepcopy(JSON_SCHEMA_OBJECT_TYPE)
    add_schema_template_properties = add_schema_array_obj[
        'items']['properties']
    update_schema_property_object = deepcopy(JSON_SCHEMA_UPDATE_PROPERTY_TYPE)
    update_schema_template_properties = update_schema_property_object[
        'additionalProperties']['properties']
    for field in template[FIELD_KEY]:
        try:
            field_name = field[TAG_NAME_KEY]
            field_type = field[PAGEFORMS_FORM_INPUT_KEY][INPUT_TYPE_KEY]
            field_smw_property = field[SMW_PROPERTY_KEY]
        except KeyError:
            continue
        else:
            if field_type.startswith(TEXT_STR):
                add_schema_template_properties[field_name] = deepcopy(
                    JSON_SCHEMA_STR_TYPE)
                update_schema_template_properties[field_name] = deepcopy(
                    JSON_SCHEMA_STR_TYPE)
            elif field_type == DROPDOWN_STR:
                enum_obj = deepcopy(JSON_SCHEMA_ENUM_TYPE)
                if ALLOWED_VALUE_KEY in field_smw_property:
                    dropdown_items = field_smw_property[ALLOWED_VALUE_KEY]
                    enum_obj['enum'] = dropdown_items
                    add_schema_template_properties[field_name] = enum_obj
                    update_schema_template_properties[field_name] = enum_obj
                else:
                    add_schema_template_properties[field_name] = deepcopy(
                        JSON_SCHEMA_STR_TYPE)
                    update_schema_template_properties[field_name] = deepcopy(
                        JSON_SCHEMA_STR_TYPE)
            elif field_type == TOKENS_STR:
                new_array_obj = deepcopy(JSON_SCHEMA_ARRAY_TYPE)
                enum_obj = deepcopy(JSON_SCHEMA_ENUM_TYPE)
                if ALLOWED_VALUE_KEY in field_smw_property:
                    dropdown_items = field_smw_property[ALLOWED_VALUE_KEY]
                    enum_obj['enum'] = dropdown_items
                    new_array_obj['items'] = enum_obj
                    add_schema_template_properties[field_name] = new_array_obj
                    update_schema_template_properties[field_name] = new_array_obj
                else:
                    add_schema_template_properties[field_name] = deepcopy(
                        JSON_SCHEMA_STR_TYPE)
                    update_schema_template_properties[field_name] = deepcopy(
                        JSON_SCHEMA_STR_TYPE)
    service_add_schema['properties'][template_name] = add_schema_array_obj
    service_update_schema['properties'][template_name] = \
        update_schema_property_object
# import json
# print(json.dumps(service_add_schema, indent=4, ensure_ascii=False))
# print(service_add_schema)
yaml.Dumper.ignore_aliases = lambda *args: True
output_path = '../diavlos/web/'
services_add_schema_file = f'{output_path}services_add_schema.yaml'
services_update_schema_file = f'{output_path}services_update_schema.yaml'
with open(services_add_schema_file, 'w+') as f:
    yaml.dump(service_add_schema, f, allow_unicode=True,
              default_flow_style=False)
with open(services_update_schema_file, 'w+') as f:
    yaml.dump(service_update_schema, f, allow_unicode=True,
              default_flow_style=False)
