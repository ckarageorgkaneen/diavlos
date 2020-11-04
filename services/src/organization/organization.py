import logging
import pickle
import re
import requests

from mwtemplates import TemplateEditor

from xml.sax.saxutils import escape

from services.data import INOUT_FILES

from services.src.site import Site

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

CATEGORY_PREFIX = '[[Category:'


class OrganizationError(Exception):
    pass


def _error(message):
    logger.error(message)
    raise OrganizationError(message)


def _cli_command(func):
    func.is_cli_command = True
    return func


def _pickle(data, file):
    with open(file, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


def _unpickle(file):
    with open(file, 'rb') as f:
        return pickle.load(f)


def _fetch_data(fetch_func, pickle_data_to_file=None):
    data = fetch_func()
    if pickle_data_to_file is not None:
        logger.debug('Pickling data...')
        _pickle(data, pickle_data_to_file)
        logger.debug('Pickled data.')
    return data


def _data(file, fetch_from_api_func, fetch_from_api=False):
    if fetch_from_api:
        data = _fetch_data(fetch_from_api_func, pickle_data_to_file=file)
    else:
        try:
            data = _unpickle(file)
        except FileNotFoundError:
            data = _fetch_data(fetch_from_api_func, pickle_data_to_file=file)
    return data


def _add_text_to_page(page, text, replace_text=None):
    new_text = None
    debug_message = None
    debug_msg_template = '{page_name_text} now contains {text_text}'
    if page is not None:
        if page.exists:
            page_text = page.text()
            if replace_text is not None and \
                    replace_text in page_text:
                # If replace_text in page text replace it
                new_text = page_text.replace(replace_text, text)
                debug_message = debug_msg_template.format(
                    page_name_text=page.name,
                    text_text=new_text)
                debug_message += f', which replaced {replace_text}'
            elif CATEGORY_PREFIX not in page_text:
                # If no category in page text
                new_text = text
        else:
            new_text = text
        if new_text is not None:
            page.edit(new_text)
            if debug_message is None:
                debug_message = debug_msg_template.format(
                    page_name_text=page.name,
                    text_text=new_text)
            logger.debug(debug_message)


def _dict_from_api_endpoint(endpoint):
    return {
        datum['id']: datum['description']
        for datum in requests.get(endpoint).json()['data']
    }

class Organization:

    # API
    API_BASE_URL = 'https://hr.apografi.gov.gr/api'
    ORGS_ENDPOINT = f'{API_BASE_URL}/public/organizations'
    SEARCH_ORG_ENDPOINT = f'{ORGS_ENDPOINT}/search'
    DICT_ENDPOINT = f'{API_BASE_URL}/public/metadata/dictionary'
    PURPOSES_DICT_ENDPOINT = f'{DICT_ENDPOINT}/Functions'
    TYPES_DICT_ENDPOINT = f'{DICT_ENDPOINT}/OrganizationTypes'
    # Files
    ALL_ORGS_PICKLE_FILE = INOUT_FILES['org_all']
    HIERARCHY_PICKLE_FILE = INOUT_FILES['org_hierarchy']
    DETAILS_PICKLE_FILE = INOUT_FILES['org_details']
    # Mediawiki
    CATEGORY_NAME = 'Φορείς'
    CATEGORY = f'[[Category:{CATEGORY_NAME}]]'
    CATALOGUE_CATEGORY = '[[Category:Κατάλογος Φορέων]]'
    NAMESPACE = 'Φορέας'
    NAMESPACE_NUMBER = 9000
    TEMPLATE_FIELD_NAME_SUFFIXES = [
        'code',
        'preferredLabel',
        'alternativeLabels',
        'description',
        'url',
        'contactPoint_telephone',
        'contactPoint_email',
        'mainAddress_fullAddress',
        'mainAddress_postCode',
        'subOrganizationOf',
        'identifier',
        'purpose',
        'vatId',
        'status',
        'foundationDate',
        'terminationDate',
        'organizationType',
    ]
    TEMPLATE_NAME = 'Φορέας'
    TEMPLATE_PARAM_PREFIX = 'gov_org_'
    template_parameters = []
    for key in TEMPLATE_FIELD_NAME_SUFFIXES:
        template_parameters.append(f'|{TEMPLATE_PARAM_PREFIX}{key}=')
    TEMPLATE_PARAMETERS_TEXT = ''.join(template_parameters)
    TEMPLATE = f'{{{{{TEMPLATE_NAME}{TEMPLATE_PARAMETERS_TEXT}}}}}'
    # Miscellaneous
    STATUS_TRANSLATION = {
        'Active': 'Ενεργός',
        'Inactive': 'Ανενεργός'
    }

    def __init__(self):
        self._site = Site()
        self._site.login()
        # Dictionaries
        self.__data_by_code = {}
        self.__name_by_code = {}
        self.__code_by_name = {}
        self.__purpose_by_id = None
        self.__type_by_id = None

    @property
    def _purpose_by_id(self):
        if self.__purpose_by_id is None:
            self.__purpose_by_id = _dict_from_api_endpoint(
                self.PURPOSES_DICT_ENDPOINT)
        return self.__purpose_by_id

    @property
    def _type_by_id(self):
        if self.__type_by_id is None:
            self.__type_by_id = _dict_from_api_endpoint(
                self.TYPES_DICT_ENDPOINT)
        return self.__type_by_id

    def _data_by_code(self, code):
        data = self.__data_by_code.get(code)
        if data is None:
            try:
                self.__data_by_code[code] = requests.get(
                    f'{self.ORGS_ENDPOINT}/{code}').json()['data']
            except Exception:
                logger.error(f'No data found for org: {code}')
            else:
                data = self.__data_by_code.get(code)
        return data

    def _name_by_code(self, code):
        name = self.__name_by_code.get(code)
        if name is None:
            data = self._data_by_code(code)
            if data is not None:
                name = data['preferredLabel']
                self.__name_by_code[code] = name
        return name

    def _code_by_name(self, name):
        code = self.__code_by_name.get(name)
        if code is None:
            self.__code_by_name = {
                ' '.join(org_dict['preferredLabel'].split()): org_dict['code']
                for org_dict in self._all()
            }
            code = self.__code_by_name.get(name)
        return code

    def _get_site_page(self, name, is_category=False):
        try:
            return self._site.categories[name] if is_category else \
                self._site.pages[name]
        except Exception as e:
            logger.error(e, name)
            return None

    def _fetch_all_from_api(self):
        logger.debug('Fetching all orgs from API...')
        all_orgs = requests.get(self.ORGS_ENDPOINT).json()['data']
        logger.debug('Fetched all orgs.')
        return all_orgs

    def _fetch_hierarchy_from_api(self):
        logger.debug('Fetching org hierarchy from API...')
        all_orgs = self._all()
        parent_children_orgs = {}
        for org_dict in all_orgs:
            parent_code = org_dict.get('subOrganizationOf')
            if parent_code is None:
                # parent_code does not exist, org_dict contains a root body
                orgcode = org_dict['code']
                if orgcode not in parent_children_orgs:
                    parent_children_orgs[orgcode] = {
                        org_dict['preferredLabel']: []}
            else:
                parentbody = parent_children_orgs.get(parent_code)
                if parentbody is None:
                    # Parent body does not exist
                    # Look in api orgs
                    for org2 in all_orgs:
                        if org2['code'] == parent_code:
                            # Found parent body, add child body
                            parent_children_orgs[parent_code] = {
                                org2['preferredLabel']: [
                                    org_dict['preferredLabel']]
                            }
                            break
                else:
                    # Parent body already exists, append child body
                    parentbody[next(iter(parentbody))].append(
                        org_dict['preferredLabel'])
                    parent_children_orgs[parent_code] = parentbody
        hierarchy = {}
        for parentcode, parent_children_dict in parent_children_orgs.items():
            hierarchy[next(iter(parent_children_dict))] = \
                list(parent_children_dict.values())[0]
        logger.debug('Fetched org hierarchy.')
        return hierarchy

    def _fetch_details_from_api(self):
        logger.debug('Fetching org details from API...')
        details = {}
        for org in self._all_page_names(without_namespace=True):
            code = self._code_by_name(org)
            if code is None:
                continue
            data = self._data_by_code(code)
            if data is None:
                continue
            details[org] = data
            # Replace parent code with parent name (preferredLabel)
            parent_code = details[org].get('subOrganizationOf')
            if parent_code:
                parent_name = self._name_by_code(parent_code)
                if parent_name is None:
                    parent_name = ''
                details[org]['subOrganizationOf'] = parent_name
            purpose_ids = details[org].get('purpose')
            # Replace purpose ids with purpose (function) names
            if purpose_ids:
                details[org]['purpose'] = ','.join([
                    self._purpose_by_id[id_] for id_ in purpose_ids])
            # Replace status with greek translation
            status = details[org].get('status')
            if status:
                details[org]['status'] = self.STATUS_TRANSLATION[status]
            # Replace type id with type name
            type_id = details[org].get('organizationType')
            if type_id:
                details[org]['organizationType'] = self._type_by_id[type_id]
            logger.debug(f'{org} - fetched details')
        logger.debug('Fetched org details.')
        return details

    def _all(self, fetch_from_api=False):
        return _data(self.ALL_ORGS_PICKLE_FILE,
                     self._fetch_all_from_api,
                     fetch_from_api=fetch_from_api)

    def _hierarchy(self, fetch_from_api=False):
        return _data(self.HIERARCHY_PICKLE_FILE,
                     self._fetch_hierarchy_from_api,
                     fetch_from_api=fetch_from_api)

    def _details(self, fetch_from_api=False):
        return _data(self.DETAILS_PICKLE_FILE,
                     self._fetch_details_from_api,
                     fetch_from_api=fetch_from_api)

    def _all_page_names(self, without_namespace=False):
        action = 'query'
        list_param = 'allpages'
        continue_param = 'continue'
        apcontinue_param = 'apcontinue'
        kwargs = {
            'format': 'json',
            'list': list_param,
            'apnamespace': self.NAMESPACE_NUMBER,
            'aplimit': 5000
        }
        page_names = []
        continue_value = 0
        while continue_value is not None:
            answer = self._site.api(action, **kwargs)
            continue_value = answer.get(
                continue_param, {}).get(apcontinue_param)
            kwargs[apcontinue_param] = continue_value
            page_names += [page_result['title']
                           for page_result in answer[action][list_param]]
        if without_namespace:
            page_names = [name.replace(f'{self.NAMESPACE}:', '')
                          for name in page_names]
        return page_names

    def _all_pages(self):
        for name in self._all_page_names():
            page = self._get_site_page(name)
            if page is not None:
                yield page

    def _create_pages(self, name, parent_category=None):
        if parent_category is None:
            parent_category = self.CATEGORY
            replace_text = None
        else:
            replace_text = self.CATEGORY
        category_page = self._get_site_page(name, is_category=True)
        _add_text_to_page(category_page, parent_category,
                          replace_text=replace_text)
        page = self._get_site_page(f'{self.NAMESPACE}:{name}')
        _add_text_to_page(page, self.CATALOGUE_CATEGORY)

    @_cli_command
    def recreate_tree(self):
        logger.debug('Creating organization category tree and pages...')
        for parent, children in self._hierarchy().items():
            self._create_pages(parent)
            parent_category = f'[[Category:{parent}]]'
            for child in children:
                self._create_pages(
                    child, parent_category=parent_category)
        logger.debug('Done.')

    @_cli_command
    def nuke_tree(self):
        logger.debug('Nuking organization category tree and pages...')

        def recurse_delete(page):
            if page.exists:
                page_is_category = True
                try:
                    page_members = page.members()
                except AttributeError:
                    # page is not a category (no members)
                    page_is_category = False
                else:
                    # page is a category
                    for member in page_members:
                        recurse_delete(member)
                finally:
                    if page_is_category or page.name.startswith(
                            self.NAMESPACE):
                        page.delete()
                        logger.debug(f'{page.name} deleted.')
        root_category_page = self._site.categories[self.CATEGORY_NAME]
        for page in root_category_page.members():
            recurse_delete(page)
        logger.debug('Done.')

    @_cli_command
    def update_pages(self):
        logger.debug('Updating organization pages...')

        def template_text(org_details):
            te = TemplateEditor(self.TEMPLATE)
            template = te.templates[self.TEMPLATE_NAME][0]
            # Add details to template parameters
            for key in self.TEMPLATE_FIELD_NAME_SUFFIXES:
                if '_' in key:
                    details_keys = key.split('_')
                else:
                    details_keys = None
                if details_keys is None:
                    value = org_details.get(key, None)
                else:
                    value = org_details.get(details_keys[0], {}).get(
                        details_keys[1], None)
                if value is not None:
                    if isinstance(value, list):
                        value = ','.join(value)
                    clean_value = escape(str(value))
                    template.parameters[
                        f'{self.TEMPLATE_PARAM_PREFIX}{key}'] = clean_value
            return str(template).replace(' |', '|')
        for org, org_details in self._details().items():
            page = self._get_site_page(f'{self.NAMESPACE}:{org}')
            if page is not None and page.exists:
                page_text = page.text()
                page_text_leftovers = re.sub(
                    rf'{{{{{self.TEMPLATE_NAME}[^{{}}]+}}}}', '',
                    page_text).strip()
                new_template_text = template_text(org_details)
                new_page_text = f'{new_template_text}\n{page_text_leftovers}'
                page.edit(new_page_text)
                logger.debug(f'{page.name} updated')
        logger.debug('Done.')
