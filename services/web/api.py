import functools

import jsonschema

from flask import Flask
from flask import jsonify
from flask import request
from flask_httpauth import HTTPBasicAuth

from services.src.eparavolo import eParavolo
from services.src.eparavolo.error import eParavoloErrorCode
from services.src.eparavolo.error import eParavoloErrorData
from services.src.helper.error import ErrorCode
from services.src.organization import Organization
from services.src.service import Service
from services.src.service import ServiceError
from services.src.service.error import ServiceErrorData

app = Flask(__name__)
auth = HTTPBasicAuth()
service = Service()
eparavolo = eParavolo()
organization = Organization()


add_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "fields": {
            "type": "object",
            "patternProperties": {
                "^.*$": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "patternProperties": {
                            "^.*$": {"type": "string"}
                        }
                    }
                }
            },
        }
    },
    "required": ["name", "fields"]
}

update_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "fields": {
            "patternProperties": {
                "^.*$": {
                    "additionalProperties": False,
                    "type": "object",
                    "patternProperties": {
                        "^[1-9][0-9]*$": {
                            "patternProperties": {
                                "^.*$": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    },
    "required": ["fields"],
    "oneOf": [
        {"required": ["name"]},
        {"required": ["uuid"]},
        {"required": ["id"]},
    ],
}

VALIDATION_ERROR_MSG = 'Ακατάλληλο σχήμα json.'


def validate_schema(schema):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                jsonschema.validate(instance=request.json, schema=schema)
            except jsonschema.exceptions.ValidationError:
                result = VALIDATION_ERROR_MSG
            else:
                result = func(**request.json)
            return result
        return wrapper
    return decorator


def make_response(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str):
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


@auth.verify_password
def service_site_login(username, password):
    try:
        service.site_login(username, password)
    except ServiceError:
        result = False
    else:
        result = True
    return result


@app.route("/api/public/services")
@make_response
def fetch_all_services():
    all_info = request.args.get('all_info')
    continue_value = request.args.get('continue')
    limit_value = request.args.get('limit')
    kwargs = {}
    if all_info:
        kwargs['fetch_all_info'] = all_info.endswith('rue')
    if continue_value:
        kwargs['continue_value'] = continue_value
    if limit_value:
        kwargs['limit_value'] = limit_value
    return service.fetch_all(**kwargs)


@app.route("/api/public/service")
@make_response
def fetch_service():
    name = request.args.get('name')
    uuid = request.args.get('uuid')
    id_ = request.args.get('id')
    bpmn = request.args.get('bpmn')
    if bpmn == 'digital':
        fetch_bpmn_digital_steps = True
    elif bpmn == 'manual':
        fetch_bpmn_digital_steps = False
    else:
        fetch_bpmn_digital_steps = None
    service_id = uuid or id_
    if name:
        result = service.fetch_by_name(
            name, fetch_bpmn_digital_steps=fetch_bpmn_digital_steps)
    elif service_id:
        result = service.fetch_by_id(
            id_=service_id,
            is_uuid=bool(uuid),
            fetch_bpmn_digital_steps=fetch_bpmn_digital_steps)
    else:
        result = 'Υποχρεωτική παράμετρος: name ή uuid.'
    return result


@app.route("/api/public/service/add", methods=['POST'])
@auth.login_required
@make_response
@validate_schema(add_schema)
def add_service(name, fields):
    return service.add(name, fields)


@app.route("/api/public/service/update", methods=['POST'])
@auth.login_required
@make_response
@validate_schema(update_schema)
def update_service(**kwargs):
    name = kwargs.get('name')
    uuid = kwargs.get('uuid')
    id_ = kwargs.get('id')
    fields = kwargs.get('fields')
    if name:
        result = service.update(name, fields)
    else:
        service_id = uuid or id_
        result = service.update_by_id(service_id, fields, is_uuid=bool(uuid))
    return result


@app.route("/api/public/paravolo/<int:code>")
@make_response
def paravolo(code: int):
    return eparavolo.fetch(code)


@app.route("/api/public/organization/units")
@make_response
def organization_units():
    name = request.args.get('name')
    unit_types = request.args.get('unit_types')
    if unit_types is not None:
        try:
            unit_types = [int(unit_type)
                          for unit_type in unit_types.split(',')]
        except ValueError:
            unit_types = None
    if name:
        result = organization.units(name, unit_types=unit_types)
    else:
        result = 'Υποχρεωτική παράμετρος: name'
    return result
