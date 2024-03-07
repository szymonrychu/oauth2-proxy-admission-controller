import base64
import copy
import http
# import json
# import random
import logging
import jsonpatch

from models import WebhookRequest, WebhookResponse

from fastapi import FastAPI
app = FastAPI()


@app.post("/mutate", response_model=WebhookResponse, response_model_exclude_none=True)
async def mutate(request:WebhookRequest):
    response = WebhookResponse()
    response.api_version = request.api_version
    response.kind = request.kind
    response.response.uid = request.request.uid
    response.response.allowed = True

    pod_body = copy.deepcopy(request.request.object)
    pod_body.metadata['labels'] = {'test': 'succesful'}

    response.response.patch_type = 'JSONPatch'
    generated_jsonpatch = jsonpatch.make_patch(request.request.object.model_dump(), pod_body.model_dump())
    print(generated_jsonpatch.to_string())
    response.response.patch = base64.b64encode(generated_jsonpatch.to_string().encode()).decode()
    return response


@app.get("/healthz/live")
def liveness():
    return ''

@app.get("/healthz/ready")
def readiness():
    return ''

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)  # pragma: no cover