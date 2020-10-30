import logging
import mwclient
import mwtemplates

from services.src.site import Site
from services.src.site import SiteError
from services.src.bpmn import BPMN


logger = logging.getLogger(__name__)


class Service:

    # General
    NAME_KEY = 'name'
    FIELDS_KEY = 'fields'
    NAMESPACE_PREFIX = 'Διαδικασία:'
    OLD_TEMPLATE_NAME = 'Διαδικασία'
    CATEGORY_NAME = 'Διαδικασίες'
    CATEGORY = f'Category:{CATEGORY_NAME}'
    TEMPLATE_NAME = 'Process'
    UUID_PROPERTY_NAME = 'Process_uuid'
    ID_PROPERTY_NAME = 'Process_id'
    BPMN_PATH = 'BPMN'

    class Error:
        UNAUTHORIZED_ACTION = {
            'message': 'Ο χρήστης δεν έχει επαρκή δικαίωματα.',
            'code': 403
        }
        FETCH_ALL = {
            'message': 'Πρόβλημα κατά τη φόρτωση των διαδικασιών.',
            'code': 404
        }
        NOT_FOUND = {
            'message': 'Η διαδικασία δε βρέθηκε.',
            'code': 200
        }
        ALREADY_EXISTS = {
            'message': 'Η διαδικασία υπάρχει ήδη.',
            'code': 409
        }
        REQUIRED_FETCH_PARAMS = {
            'message': 'Υποχρεωτική παράμετρος: name ή uuid.',
            'code': 404
        }
        REQUIRED_UPDATE_KEYS = {
            'message': 'Υποχρεωτικά κλειδιά: name, fields.',
            'code': 404
        }
        NO_FIELD_UPDATED = {
            'message': 'Δεν ενημερώθηκε κανένα πεδίο.',
            'code': 404
        }
        FIELDS_NOT_PROPER = {
            'message': 'To κλειδί fields πρέπει να περιέχει dictionary.',
            'code': 404
        }

    def __init__(self):
        self._site = Site()

    def _service_dict(self, name, template_editor):
        dict_ = {
            self.NAME_KEY: name,
            self.FIELDS_KEY: {}
        }
        fields_dict = dict_[self.FIELDS_KEY]
        for tpl_name in template_editor.templates.keys():
            tpl_instances = template_editor.templates[tpl_name]
            tpl_instances_data = {}
            for tpl_num, tpl_instance in enumerate(tpl_instances):
                tpl_instance_dict = {}
                for param in tpl_instance.parameters:
                    tpl_instance_dict[param.name] = param.value
                tpl_instances_data[tpl_num] = tpl_instance_dict
            fields_dict[tpl_name] = tpl_instances_data
        return dict_

    def _page_template_names(self, page):
        return [template.page_title for template in page.templates()]

    def _page_is_service(self, page, page_template_names):
        return self.TEMPLATE_NAME in page_template_names or \
            self.OLD_TEMPLATE_NAME in page_template_names

    def _templates_text(self, fields):
        templates_text = ''
        for tpl_name, tpl_instances in fields.items():
            for tpl_instance_fields in tpl_instances:
                template_text = f'{tpl_name}'
                for field_name, field_value in tpl_instance_fields.items():
                    template_text += f'|{field_name}={field_value}'
                template_text = f'{{{{{template_text}}}}}'
            templates_text += template_text
        return templates_text

    def move_all_pages_in_category_to_namespace(self):
        self.site_login()
        for page in self._site.categories[self.CATEGORY_NAME].members():
            page_title = page.page_title
            logger.debug(page_title)
            new_title = f'{self.NAMESPACE_PREFIX}{page_title}'
            new_page = self._site.pages[new_title]
            try:
                if not new_page.exists:
                    page.move(new_title, no_redirect=True)
                    logger.debug(f'Moved {page_title} to {new_title}')
            except Exception as e:
                logger.debug(e)

    def site_login(self, username=None, password=None):
        try:
            self._site.login(username=username, password=password)
        except SiteError:
            return False
        return True

    def fetch_all(self, limit_value=10, continue_value='',
                  fetch_all_info=False):
        try:
            mw_response = self._site.get('query', format='json',
                                         list='categorymembers',
                                         cmtitle=self.CATEGORY,
                                         cmcontinue=continue_value,
                                         cmlimit=limit_value)
        except mwclient.errors.APIError as e:
            success, result = False, e.info
        else:
            if 'continue' in mw_response:
                continue_response = mw_response['continue']['cmcontinue']
            else:
                continue_response = None
            if fetch_all_info:
                services_data = {
                    category_member['title'].replace(
                        self.NAMESPACE_PREFIX, ''):
                    self.fetch_by_name(category_member['title'])
                    for category_member in mw_response['query'][
                        'categorymembers']
                }
            else:
                services_data = [
                    category_member['title'].replace(
                        self.NAMESPACE_PREFIX, '')
                    for category_member in mw_response['query'][
                        'categorymembers']
                ]
            success, result = True, {
                'continue': continue_response,
                'services': services_data
            }
        return success, result

    def fetch_by_name(self, name, fetch_bpmn_digital_steps=None):
        success, result = False, self.Error.NOT_FOUND
        page = self._site.pages[name]
        if page.exists:
            page = page.resolve_redirect()
            page_template_names = self._page_template_names(page)
            if self._page_is_service(page, page_template_names):
                service_dict = self._service_dict(
                    name, mwtemplates.TemplateEditor(page.text()))
                if fetch_bpmn_digital_steps is None:
                    data = service_dict
                else:
                    data = BPMN(
                        digital_steps=fetch_bpmn_digital_steps).xml(
                        service_dict).replace('\n', '').replace(
                        '\t', '').replace('\"', '\'')
                success, result = bool(data), data
        return success, result

    def fetch_by_id(self, id_, id_is_uuid=False,
                    fetch_bpmn_digital_steps=None):
        property_name = self.UUID_PROPERTY_NAME \
            if id_is_uuid else self.ID_PROPERTY_NAME
        askargs_conditions = f'{property_name}::{id_}'
        try:
            site_response = self._site.get(
                'askargs', format='json',
                conditions=askargs_conditions)
        except mwclient.errors.APIError as e:
            success, result = False, e.info
        else:
            site_response_results = site_response['query']['results']
            if len(site_response_results) == 1:
                service_name = next(iter(site_response_results))
                success, result = self.fetch_by_name(
                    service_name,
                    fetch_bpmn_digital_steps=fetch_bpmn_digital_steps)
            else:
                success, result = False, self.Error.NOT_FOUND
        return success, result

    def update(self, name, fields):
        page = self._site.pages[name]
        page_template_names = self._page_template_names(page)
        if not (page.exists and self._page_is_service(
                page, page_template_names)):
            success, result = False, self.Error.NOT_FOUND
        elif not page.can('edit'):
            success, result = False, self.Error.UNAUTHORIZED_ACTION
        elif not isinstance(fields, dict):
            success, result = False, self.Error.FIELDS_NOT_PROPER
        else:
            te = mwtemplates.TemplateEditor(page.text())
            fields_updated = False
            for tpl_name, tpl_instances_dict in fields.items():
                if tpl_name in page_template_names:
                    page_tpl_instances = te.templates[tpl_name]
                    for instance_num_str, instance_fields in \
                            tpl_instances_dict.items():
                        instance_num = int(instance_num_str)
                        try:
                            page_tpl = page_tpl_instances[instance_num]
                            for field_name, field_value in \
                                    instance_fields.items():
                                if field_name in page_tpl.parameters:
                                    # Update field
                                    page_tpl.parameters[field_name] = \
                                        field_value
                                    if not fields_updated:
                                        fields_updated = True
                        except IndexError:
                            # Template instance does not exist
                            continue
            if fields_updated:
                page.edit(te.wikitext())
            if fields_updated:
                success, result = True, self._service_dict(
                    name, mwtemplates.TemplateEditor(page.text()))
            else:
                success, result = False, self.Error.NO_FIELD_UPDATED
        return success, result

    def add(self, name, fields):
        page = self._site.pages[name]
        if page.exists:
            success, result = False, self.Error.ALREADY_EXISTS
        elif not page.can('edit'):
            success, result = False, self.Error.UNAUTHORIZED_ACTION
        elif not isinstance(fields, dict):
            success, result = False, self.Error.FIELDS_NOT_PROPER
        else:
            templates_text = self._templates_text(fields)
            te = mwtemplates.TemplateEditor(templates_text)
            if te.templates:
                page.edit(te.wikitext())
                success, result = True, self._service_dict(name, te)
            else:
                success, result = False, self.Error.FIELDS_NOT_PROPER
        return success, result
