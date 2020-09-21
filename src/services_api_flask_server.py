#!/usr/bin/env python3
import mwclient
import mwtemplates

import flask

NAME_KEY = 'name'
FIELDS_KEY = 'fields'
OLD_SERVICE_TEMPLATE_NAME = 'Διαδικασία'
SERVICE_TEMPLATE_NAME = 'Process'

app = flask.Flask(__name__)


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


def get_service(name=None):
    site = mwclient.Site('diadikasies.dev.grnet.gr', scheme='http', path='/')
    # site.login('Master', '4BQpC2625FBD')
    if name is None:
        return {[page_dict(page) for page in site.allpages()]}
    else:
        page = site.pages[name]
        if page.exists:
            page = page.resolve_redirect()
            page_template_names = [
                template.page_title for template in page.templates()]
            page_is_service = SERVICE_TEMPLATE_NAME in page_template_names or \
                OLD_SERVICE_TEMPLATE_NAME in page_template_names
            if page_is_service:
                return flask.jsonify(page_dict(page, page_template_names))
        return flask.jsonify('H διαδικασία δε βρέθηκε.'), 404


@app.route("/api/public/services/<string:service_name>")
def service(service_name: str):
    return get_service(name=service_name)


if __name__ == "__main__":
    app.run()
