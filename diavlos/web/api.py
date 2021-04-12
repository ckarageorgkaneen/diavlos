#!/usr/bin/env python3
"""The web API of diavlos."""
import functools
import logging

from flask import jsonify

import connexion

from connexion.exceptions import Unauthorized

from diavlos.data import IN_FILES
from diavlos.src.eparavolo import eParavolo
from diavlos.src.eparavolo.error import eParavoloErrorCode
from diavlos.src.eparavolo.error import eParavoloErrorData
from diavlos.src.helper.error import ErrorCode
from diavlos.src.metadata import Metadata
from diavlos.src.organization import Organization
from diavlos.src.service import Service
from diavlos.src.service.error import ServiceErrorData
from diavlos.src.site import Site
from diavlos.src.site import SiteError

logging.basicConfig(level=logging.INFO)

default_site = greek_site = Site()
english_site = Site(config_file=IN_FILES['english_site_config'])
service = Service(site=default_site)
eparavolo = eParavolo()
organization = Organization()
metadata = Metadata()


def make_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str) and not result.startswith('<'):
            response = {
                'success': False,
                'message': result
            }
            status_code = 400
        elif isinstance(result, ErrorCode):
            if isinstance(result, eParavoloErrorCode):
                error_handler = eParavoloErrorData
            else:
                error_handler = ServiceErrorData
            message, status_code = error_handler(result)
            response = {
                'success': False,
                'message': message
            }
            status_code = status_code
        else:
            response = {
                'success': True,
                'result': result
            }
            status_code = 200
        return jsonify(response), status_code
    return wrapper


def handle_english_param(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'english' in kwargs:
            english = kwargs['english']
            if english:
                default_site = english_site
        else:
            default_site = greek_site
        service.set_site(default_site)
        return func(*args, **kwargs)
    return wrapper


def handle_bpmn_param(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'bpmn' in kwargs:
            bpmn = kwargs['bpmn']
            if bpmn == 'digital':
                kwargs['bpmn'] = True
            elif bpmn == 'manual':
                kwargs['bpmn'] = False
        return func(*args, **kwargs)
    return wrapper


def site_login(username, password, required_scopes=None):
    try:
        default_site.login(username, password)
    except SiteError:
        raise Unauthorized(description='Εσφαλμένα στοιχεία mediawiki')
    return {}


@make_response
def get_all_services(include_info=False, page_continue='', limit=10):
    return service.fetch_all(include_info, page_continue, limit)


@make_response
@handle_english_param
@handle_bpmn_param
def get_service_by_name(name, bpmn=None, english=False):
    return service.fetch_by_name(name, fetch_bpmn_digital_steps=bpmn)


@make_response
@handle_english_param
@handle_bpmn_param
def get_service_by_id(id, bpmn=None, english=False):
    return service.fetch_by_id(id_=id, is_uuid=False,
                               fetch_bpmn_digital_steps=bpmn)


@make_response
@handle_english_param
@handle_bpmn_param
def get_service_by_uuid(uuid, bpmn=None, english=False):
    return service.fetch_by_id(id_=uuid, is_uuid=True,
                               fetch_bpmn_digital_steps=bpmn)


@make_response
def add_service(name):
    return service.add(name, connexion.request.json)


@make_response
def update_service_by_name(name):
    return service.update(name, fields=connexion.request.json)


@make_response
def update_service_by_id(id):
    return service.update_by_id(id, fields=connexion.request.json,
                                is_uuid=False)


@make_response
def update_service_by_uuid(uuid):
    return service.update_by_id(uuid, fields=connexion.request.json,
                                is_uuid=True)


@make_response
def get_organization_units(name, types):
    return organization.units(name, unit_types=types)


@make_response
def get_paravolo(code):
    return eparavolo.fetch(code)


@make_response
def get_metadata(uuid, type):
    return metadata.read(uuid, type)


@make_response
def add_metadata(uuid, type):
    if metadata.create(uuid, type, **connexion.request.json):
        return metadata.read(uuid, type)
    else:
        return f'Υπάρχει ήδη αυτή η καταχώρηση ({uuid}, {type}).'


@make_response
def update_metadata(uuid, type):
    if metadata.update(uuid, type, **connexion.request.json):
        return metadata.read(uuid, type)
    else:
        return 'Δεν ενημερώθηκαν μεταδεδομένα.'


app = connexion.App(__name__)
app.add_api('openapi-dereferenced.yaml')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
