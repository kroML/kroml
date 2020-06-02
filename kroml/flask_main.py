from flask import Flask, request
from flask_cors import CORS, cross_origin
import json
import re
import base64

from main import MainExecution

app = Flask(__name__)
CORS(app)

main_flow = None


@app.before_first_request
def setup():
    global main_flow
    main_flow = MainExecution()

    global text_to_code
    text_to_code = MainExecution(config_json='{"main_config_file": "main_config.ini", "mode": "text_to_cod"}')


@app.route("/", methods=["GET", "POST"])
@cross_origin()
def text_to_code():
    global main_flow
    if request.method == "POST":
        req_message = request.json
        resp = main_flow.execute(req_message)
        if resp is None:
            resp = ''
        return json.dumps({"response": resp})

    elif request.method == "GET":
        return json.dumps({"response": "haf"})


@app.route("/import_file", methods=["GET", "POST"])
@cross_origin()
def import_file():
    if request.method == "POST":
        req_msg = request.json
        req_data = request.data

        req_data = re.search(b"[^,]*$", req_data).group(0)
        req_data = bytearray(req_data)
        req_data = req_data[:-2]
        req_data = bytes(req_data)
        file = base64.decodebytes(req_data + b'===')

        with open('./data/input/' + str(req_msg['name']), 'wb') as f:
            f.write(file)
            f.close()
        return "File " + str(req_msg['name']) + "has been saved."

    elif request.method == "GET":
        pass


if __name__ == "__main__":
    CORS(app)
    app.run(debug=True)

