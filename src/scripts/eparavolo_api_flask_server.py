#!/usr/bin/env python3
import yaml
import datetime
import zeep
import flask

from zeep.wsse.username import UsernameToken

with open('eparavolo_credentials.yaml') as file:
    credentials = yaml.load(file, Loader=yaml.FullLoader)

wsdl = 'https://test.gsis.gr/esbpilot/eparavoloPublicService?wsdl'
client = zeep.Client(wsdl=wsdl,
                     wsse=UsernameToken(
                         credentials['username'],
                         credentials['password']))

app = flask.Flask(__name__)


def get_paravolo(code):
    request_data = {
        'auditRecord': {
            'auditTransactionId': '',
            'auditTransactionDate': datetime.datetime.now(
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            'auditUnit': '',
            'auditProtocol': '',
            'auditUserId': '',
            'auditUserIp': '',
        },
       'getParavoloTypeInfoInputRecord': {
            'typeId': code,
            'languageId': 1,
        }
    }
    return client.service.getParavoloTypeInfo(**request_data)

@app.route("/api/public/paravolo/<int:code>")
def paravolo(code: int):
    response = get_paravolo(code)
    if response is None:
        return flask.jsonify('Paravolo not found.'), 404
    return flask.jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
