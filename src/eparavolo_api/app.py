#!/usr/bin/env python3
import yaml
import flask

from eparavolo import eParavolo

with open('eparavolo_credentials.yaml') as file:
    credentials = yaml.load(file, Loader=yaml.FullLoader)
eparavolo = eParavolo(credentials)
app = flask.Flask(__name__)


@app.route("/api/public/paravolo/<int:code>")
def paravolo(code: int):
    success, result_obj = eparavolo.fetch(code)
    if 'message' in result_obj:
        result = result_obj['message']
        code = 200  # code = result_obj['code']
    else:
        result = result_obj
        code = 200
    response = {
        'success': success,
        'result': result
    }
    return flask.jsonify(response), code


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
