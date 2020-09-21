#!/usr/bin/env python3
import mwclient
import mwtemplates
import flask

SITE_URL = 'diadikasies.dev.grnet.gr'
SITE_PATH = '/'
SITE_SCHEME = 'http'
NAME_KEY = 'name'
FIELDS_KEY = 'fields'
SERVICE_NAMESPACE_PREFIX = 'Διαδικασία:'
OLD_SERVICE_TEMPLATE_NAME = 'Διαδικασία'
SERVICES_CATEGORY = 'Category:Διαδικασίες'
SERVICE_TEMPLATE_NAME = 'Process'
SERVICE_NOT_FOUND_MSG = 'Service not found.'

mw_site = mwclient.Site(SITE_URL, scheme=SITE_SCHEME, path=SITE_PATH)
app = flask.Flask(__name__)


def get_all_services(limit_value=10, fetch_all_info=False):
    continue_value = flask.request.args.get('continue')
    limit_value = flask.request.args.get('limit') or limit_value
    try:
        mw_response = mw_site.get('query', format='json',
                                  list='categorymembers',
                                  cmtitle=SERVICES_CATEGORY,
                                  cmcontinue=continue_value,
                                  cmlimit=limit_value)
    except mwclient.errors.APIError as e:
        response = e.info
    else:
        if 'continue' in mw_response:
            continue_response = mw_response['continue']['cmcontinue']
        else:
            continue_response = None
        if fetch_all_info:
            services_data = {
                category_member['title'].replace(
                    SERVICE_NAMESPACE_PREFIX, ''): get_service_by_name(
                    category_member['title'])
                for category_member in mw_response['query'][
                    'categorymembers']
            }
        else:
            services_data = [
                category_member['title'].replace(
                    SERVICE_NAMESPACE_PREFIX, '')
                for category_member in mw_response['query'][
                    'categorymembers']
            ]
        response = {
            'continue': continue_response,
            'services': services_data}
    return response


def page_dict(page, page_template_names):
    dict_ = {
        NAME_KEY: page.page_title,
        FIELDS_KEY: {}
    }
    te = mwtemplates.TemplateEditor(page.text())
    fields_dict = dict_[FIELDS_KEY]
    for template_name in page_template_names:
        template_instances = te.templates[template_name]
        template_instances_data = []
        for template_instance in template_instances:
            template_instance_dict = {}
            for param in template_instance.parameters:
                template_instance_dict[param.name] = param.value
            template_instances_data.append(template_instance_dict)
        fields_dict[template_name] = template_instances_data
    return dict_


def get_service_by_name(name):
    page = mw_site.pages[name]
    if page.exists:
        page = page.resolve_redirect()
        page_template_names = [
            template.page_title for template in page.templates()]
        page_is_service = SERVICE_TEMPLATE_NAME in page_template_names or \
            OLD_SERVICE_TEMPLATE_NAME in page_template_names
        if page_is_service:
            return page_dict(page, page_template_names)
    return None


def get_service_by_uuid(uuid):
    try:
        mw_response = mw_site.get('askargs', format='json',
                                  conditions=f'Process_uuid::{uuid}')
    except mwclient.errors.APIError as e:
        return e.info
    else:
        mw_response_results = mw_response['query']['results']
        if len(mw_response_results) != 1:
            return None
        service_name = next(iter(mw_response_results))
    return get_service_by_name(service_name)


@app.route("/api/public/services")
def services():
    all_info = flask.request.args.get('all_info')
    if all_info:
        fetch_all_info = all_info.endswith('rue')
    else:
        fetch_all_info = False
    response = get_all_services(fetch_all_info=fetch_all_info)
    if response is None:
        return flask.jsonify(SERVICE_NOT_FOUND_MSG), 404
    return flask.jsonify(response)


@app.route("/api/public/service")
def service():
    name = flask.request.args.get('name')
    uuid = flask.request.args.get('uuid')
    if name:
        response = get_service_by_name(name)
    elif uuid:
        response = get_service_by_uuid(uuid)
    else:
        return flask.jsonify('Must provide a name or uuid parameter.'), 404
    if response is None:
        return flask.jsonify(SERVICE_NOT_FOUND_MSG), 404
    return flask.jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
