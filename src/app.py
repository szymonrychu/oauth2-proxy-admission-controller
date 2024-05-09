import base64
import logging
import os

import jsonpatch

from k8s import get_config
from pod import patch_pod

logging.basicConfig(level=logging.DEBUG)

from fastapi import FastAPI, Request, Response

from models import (V1AdmissionReviewRequest, V1AdmissionReviewResponse,
                    get_admission_resp_from_req)

app = FastAPI()

@app.post("/mutate", response_model=V1AdmissionReviewResponse, response_model_exclude_none=True, response_model_by_alias=True, response_model_exclude_unset=True)
async def mutate(request:V1AdmissionReviewRequest) -> V1AdmissionReviewResponse:
    response = get_admission_resp_from_req(request)
    response.response.patch_type = 'JSONPatch'
    response.response.patch = 'W10=' # base64.b64encode('[]'.encode("ascii"))

    pod = request.request.object
    configuration_secret_name = pod.metadata.annotations.get('oauth2-proxy-admission/configuration-secret-name', None)
    configuration_secret_namespace = pod.metadata.annotations.get('oauth2-proxy-admission/configuration-secret-namespace', None)
    config = get_config(configuration_secret_name, configuration_secret_namespace)
    if not config:
        return response
        
    config.patch_container_name = pod.metadata.annotations.get('oauth2-proxy-admission/container-name', None)
    config.patch_port_number = pod.metadata.annotations.get('oauth2-proxy-admission/port-number', None)
    config.patch_port_name = pod.metadata.annotations.get('oauth2-proxy-admission/port-name', None)

    patched_pod = patch_pod(pod, config)
    patch = jsonpatch.make_patch(pod.dict(skip_defaults=True), patched_pod.dict(skip_defaults=True)).to_string()
    response.response.patch = base64.b64encode(patch.encode("ascii"))
    return response


@app.get("/healthz/live")
async def liveness():
    return Response('{}', status_code=200)

@app.get("/healthz/ready")
async def readiness():
    return Response('{}', status_code=200)
