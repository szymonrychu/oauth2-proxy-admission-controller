import base64
import copy
import http
import json
import random
import logging

import jsonpatch
from flask import Flask, jsonify, request

app = Flask(__name__)
app.logger.setLevel(logging.INFO)


@app.route("/validate", methods=["POST"])
def validate():
    allowed = True
    try:
        for container_spec in request.json["request"]["object"]["spec"]["containers"]:
            if "env" in container_spec:
                allowed = False
    except KeyError:
        pass
    return jsonify(
        {
            "response": {
                "allowed": allowed,
                "uid": request.json["request"]["uid"],
                "status": {"message": "env keys are prohibited"},
            }
        }
    )

@app.route("/mutate", methods=["POST"])
def mutate():
    request_info = request.get_json()
    uid = request_info["request"].get("uid")
    api_version = request_info.get("apiVersion")
    kind = request_info.get("kind")
    response = {
        "kind": kind,
        "apiVersion": api_version,
        "response": {
            "uid": uid,
            "allowed": True,
            "status": {
                "message": "TEST message"
            },
            "patchType": "JSONPatch",
            "patch": base64.b64encode(jsonpatch.JsonPatch([{"op": "add", "path": "/metadata/labels/allow", "value": "yes"}]).to_string().encode("utf-8")).decode("utf-8")
        }
    }
    return jsonify(response)


@app.route("/healthz/live", methods=["GET"])
def liveness():
    return ("", http.HTTPStatus.NO_CONTENT)

@app.route("/healthz/ready", methods=["GET"])
def readiness():
    return ("", http.HTTPStatus.NO_CONTENT)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)  # pragma: no cover