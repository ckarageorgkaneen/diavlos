import logging
import mwclient
from mwtemplates import TemplateEditor

from .error import ServiceErrorCode as ErrorCode
from services.src.site import Site
from services.src.site import SiteError
from services.src.bpmn import BPMN

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """ServiceError exception"""


def _error(message):
    logger.error(message)
    raise ServiceError(message)


def _template_text(template_name, template_instance):
    template_text = template_name
    for field_name, field_value in template_instance.items():
        template_text += f'\n |{field_name}={field_value}'
    return f'{{{{{template_text}\n}}}}\n'

class Service:

    # General
    NAME_KEY = 'name'
    FIELDS_KEY = 'fields'
    NAMESPACE_PREFIX = 'Διαδικασία:'
    CATEGORY_NAME = 'Διαδικασίες'
    CATEGORY = f'Category:{CATEGORY_NAME}'
    TEMPLATE_NAME = 'Process'
    UUID_PROPERTY_NAME = 'Process_uuid'
    ID_PROPERTY_NAME = 'Process_id'
    BPMN_PATH = 'BPMN'

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
            for tpl_idx, tpl_instance in enumerate(tpl_instances):
                tpl_instance_dict = {}
                for param in tpl_instance.parameters:
                    tpl_instance_dict[param.name] = param.value
                tpl_instances_data[tpl_idx + 1] = tpl_instance_dict
            fields_dict[tpl_name] = tpl_instances_data
        return dict_

    def _page(self, name):
        if self.NAMESPACE_PREFIX not in name:
            name = f'{self.NAMESPACE_PREFIX}{name}'
        return self._site.pages[name]

    def _name_by_id(self, id_, is_uuid=False):
        property_name = self.UUID_PROPERTY_NAME \
            if is_uuid else self.ID_PROPERTY_NAME
        askargs_conditions = f'{property_name}::{id_}'
        try:
            site_response = self._site.get(
                'askargs', format='json',
                conditions=askargs_conditions)
        except mwclient.errors.APIError:
            result = ErrorCode.SITE_API_ERROR
        else:
            site_response_results = site_response['query']['results']
            if len(site_response_results) == 1:
                result = next(iter(site_response_results))
            else:
                result = None
        return result

    def move_all_pages_in_category_to_namespace(self):
        self.site_auto_login(auto=True)
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

    def site_auto_login(self):
        try:
            self._site.auto_login()
        except SiteError as e:
            _error(str(e))

    def site_login(self, username, password):
        result = bool(username) and bool(password)
        if not result:
            _error('Username and password must not be empty.')
        try:
            self._site.login(username=username, password=password)
        except SiteError as e:
            _error(str(e))

    def fetch_all(self, limit_value=10, continue_value='',
                  fetch_all_info=False):
        try:
            mw_response = self._site.get('query', format='json',
                                         list='categorymembers',
                                         cmtitle=self.CATEGORY,
                                         cmcontinue=continue_value,
                                         cmlimit=limit_value)
        except mwclient.errors.APIError:
            result = ErrorCode.SITE_API_ERROR
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
            result = {
                'continue': continue_response,
                'services': services_data
            }
        return result

    def fetch_by_name(self, name, fetch_bpmn_digital_steps=None):
        page = self._page(name)
        if page.exists:
            page = page.resolve_redirect()
            service_dict = self._service_dict(
                name, TemplateEditor(page.text()))
            if fetch_bpmn_digital_steps is None:
                data = service_dict
            else:
                data = BPMN(
                    digital_steps=fetch_bpmn_digital_steps).xml(
                    service_dict).replace('\n', '').replace(
                    '\t', '').replace('\"', '\'')
            result = data
        else:
            result = ErrorCode.NOT_FOUND
        return result

    def fetch_by_id(self, id_, is_uuid=False,
                    fetch_bpmn_digital_steps=None):
        service_name = self._name_by_id(id_, is_uuid=is_uuid)
        if service_name is None:
            result = ErrorCode.NOT_FOUND
        else:
            result = self.fetch_by_name(
                service_name,
                fetch_bpmn_digital_steps=fetch_bpmn_digital_steps)
        return result

    def update_by_id(self, id_, fields, is_uuid=False):
        service_name = self._name_by_id(id_, is_uuid=is_uuid)
        if service_name is None:
            result = ErrorCode.NOT_FOUND
        else:
            result = self.update(service_name, fields)
        return result

    def update(self, name, fields):
        page = self._page(name)
        if not page.can('edit'):
            result = ErrorCode.UNAUTHORIZED_ACTION
        elif page.exists:
            te = TemplateEditor(page.text())
            fields_updated = False
            for tpl_name, tpl_instances in fields.items():
                template_names = te.templates.keys()
                if tpl_name in template_names:
                    page_tpl_instances = te.templates[tpl_name]
                    # Update template instances
                    for instance_num_str, tpl_instance in \
                            tpl_instances.items():
                        instance_num = int(instance_num_str)
                        try:
                            page_tpl = page_tpl_instances[instance_num - 1]
                        except IndexError:
                            # Template instance does not exist, create it
                            if instance_num > len(page_tpl_instances):
                                # Only if numbering is greater than the last
                                # existing instance number
                                new_tpl_text = _template_text(
                                    tpl_name, tpl_instance)
                                if new_tpl_text:
                                    new_wiki_text = ''
                                    for name, tpls in te.templates.items():
                                        for tpl in tpls:
                                            new_wiki_text += f'{str(tpl)}\n'
                                        if name == tpl_name:
                                            new_wiki_text += \
                                                f'{new_tpl_text}'
                                    if new_wiki_text:
                                        te = TemplateEditor(new_wiki_text)
                                        if not fields_updated:
                                            fields_updated = True
                        else:
                            for field_name, field_value in \
                                    tpl_instance.items():
                                # Update or create field
                                page_tpl.parameters[field_name] = \
                                    field_value
                                if not fields_updated:
                                    fields_updated = True
                else:
                    new_templates_text = ''
                    for instance_num_str, tpl_instance in \
                            tpl_instances.items():
                        new_templates_text += _template_text(
                            tpl_name, tpl_instance)
                    if new_templates_text:
                        # Append new templates to wiki text
                        new_wiki_text = \
                            f'{te.wikitext()}\n{new_templates_text}'
                        te = TemplateEditor(new_wiki_text)
                        if not fields_updated:
                            fields_updated = True
            if fields_updated:
                wikitext = te.wikitext().replace('\n\n', '\n')
                if wikitext[0] == '\n':
                    wikitext = wikitext[1:]
                page.edit(wikitext)
                result = self._service_dict(
                    name, TemplateEditor(page.text()))
            else:
                result = ErrorCode.NO_FIELD_UPDATED
        else:
            result = ErrorCode.NOT_FOUND
        return result

    def add(self, name, fields):
        page = self._page(name)
        if page.exists:
            result = ErrorCode.ALREADY_EXISTS
        elif not page.can('edit'):
            result = ErrorCode.UNAUTHORIZED_ACTION
        else:
            templates_text = ''
            for tpl_name, tpl_instances in fields.items():
                for tpl_instance in tpl_instances:
                    templates_text += _template_text(tpl_name, tpl_instance)
            te = TemplateEditor(templates_text)
            if te.templates:
                page.edit(te.wikitext())
                result = self._service_dict(name, te)
            else:
                result = ErrorCode.INVALID_TEMPLATE
        return result
