import base64
import logging
import os

import jsonpatch
from pydantic import ValidationError
from kubernetes.client.exceptions import ApiException

from k8s import (b64enc, find_pods_services, generate_proxy_container,
                 get_config, get_container_port, get_pod_container,
                 revert_services, update_services)

logging.basicConfig(level=logging.DEBUG)

from copy import deepcopy

from fastapi import FastAPI, Request, Response

from log import logger
from models import (V1AdmissionReviewRequest, V1AdmissionReviewResponse,
                    get_admission_resp_from_req)

app = FastAPI()

@app.post("/mutate", response_model=V1AdmissionReviewResponse, response_model_exclude_none=True, response_model_by_alias=True, response_model_exclude_unset=True)
async def mutate(request:V1AdmissionReviewRequest) -> V1AdmissionReviewResponse:
    response = get_admission_resp_from_req(request)

    pod = request.request.object
    configuration_secret_name = pod.metadata.annotations.get('oauth2-proxy-admission/configuration-secret-name', None)
    configuration_secret_namespace = pod.metadata.annotations.get('oauth2-proxy-admission/configuration-secret-namespace', None)
    config = None
    try:
        config = get_config(configuration_secret_name, configuration_secret_namespace)
    except ApiException:
        logger.info("Couldn't load config from k8s- configuration error, forbidding!")
        response.response.allowed = False
        return response
    except ValidationError:
        logger.info("Couldn't parse config!")
        revert_services(pod)
        return response
    
        
    config.patch_container_name = pod.metadata.annotations.get('oauth2-proxy-admission/container-name', None)
    config.patch_port_number = pod.metadata.annotations.get('oauth2-proxy-admission/port-number', None)
    config.patch_port_name = pod.metadata.annotations.get('oauth2-proxy-admission/port-name', None)
    
    container = get_pod_container(pod, config)
    if not container:
        logger.info("Couldn't load container!")
        revert_services(pod)
        return response
    
    port = get_container_port(container, config)
    if not port:
        logger.info("Couldn't load port!")
        revert_services(pod)
        return response
    
    service = find_pods_services(pod, port)
    if not service:
        logger.info("Couldn't load service!")
        revert_services(pod)
        return response

    old_pod = deepcopy(pod)
    pod.spec.containers.append(generate_proxy_container(port.containerPort, port.name, config))

    update_services(service, port, pod)


    if container.readinessProbe.httpGet.port and container.readinessProbe.httpGet.port == port.name:
        container.readinessProbe.httpGet.port = f"{port.name}-insecure"
    elif container.readinessProbe.tcpSocket.port and container.readinessProbe.tcpSocket.port == port.name:
        container.readinessProbe.tcpSocket.port = f"{port.name}-insecure"

    if container.livenessProbe.httpGet.port and container.livenessProbe.httpGet.port == port.name:
        container.livenessProbe.httpGet.port = f"{port.name}-insecure"
    elif container.livenessProbe.tcpSocket.port and container.livenessProbe.tcpSocket.port == port.name:
        container.livenessProbe.tcpSocket.port = f"{port.name}-insecure"

    if container.startupProbe.httpGet.port and container.startupProbe.httpGet.port == port.name:
        container.startupProbe.httpGet.port = f"{port.name}-insecure"
    elif container.startupProbe.tcpSocket.port and container.startupProbe.tcpSocket.port == port.name:
        container.startupProbe.tcpSocket.port = f"{port.name}-insecure"

    port.name = f"{port.name}-insecure"
    response.response.patch_type = 'JSONPatch'
    patch = jsonpatch.make_patch(old_pod.dict(skip_defaults=True), pod.dict(skip_defaults=True)).to_string()
    response.response.patch = b64enc(patch)    
    return response


@app.get("/healthz/live")
async def liveness():
    return Response('{}', status_code=200)

@app.get("/healthz/ready")
async def readiness():
    return Response('{}', status_code=200)
