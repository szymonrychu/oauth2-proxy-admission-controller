import logging
import jsonpatch
from config import load_config
from service_operations import revert_services, update_services
from pod_operations import (
    get_container_port,
    get_pod_container,
    find_pods_services,
    generate_proxy_container,
)
from utils import b64enc
from copy import deepcopy
from fastapi import FastAPI, Response
from log import logger
from models import (
    V1AdmissionReviewRequest,
    V1AdmissionReviewResponse,
    get_admission_resp_from_req,
)

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()


@app.post(
    "/mutate",
    response_model=V1AdmissionReviewResponse,
    response_model_exclude_none=True,
    response_model_by_alias=True,
    response_model_exclude_unset=True,
)
async def mutate(request: V1AdmissionReviewRequest) -> V1AdmissionReviewResponse:
    response = get_admission_resp_from_req(request)
    pod = request.request.object

    config = load_config(pod)

    if not config:
        revert_services(pod)
        return response

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
    pod.spec.containers.append(
        generate_proxy_container(port.containerPort, port.name, config)
    )

    if (
        container.readinessProbe.httpGet.port
        and container.readinessProbe.httpGet.port == port.name
    ):
        container.readinessProbe.httpGet.port = f"{port.name}-insecure"
    elif (
        container.readinessProbe.tcpSocket.port
        and container.readinessProbe.tcpSocket.port == port.name
    ):
        container.readinessProbe.tcpSocket.port = f"{port.name}-insecure"

    if (
        container.livenessProbe.httpGet.port
        and container.livenessProbe.httpGet.port == port.name
    ):
        container.livenessProbe.httpGet.port = f"{port.name}-insecure"
    elif (
        container.livenessProbe.tcpSocket.port
        and container.livenessProbe.tcpSocket.port == port.name
    ):
        container.livenessProbe.tcpSocket.port = f"{port.name}-insecure"

    if (
        container.startupProbe.httpGet.port
        and container.startupProbe.httpGet.port == port.name
    ):
        container.startupProbe.httpGet.port = f"{port.name}-insecure"
    elif (
        container.startupProbe.tcpSocket.port
        and container.startupProbe.tcpSocket.port == port.name
    ):
        container.startupProbe.tcpSocket.port = f"{port.name}-insecure"

    port.name = f"{port.name}-insecure"
    response.response.patch_type = "JSONPatch"
    patch = jsonpatch.make_patch(
        old_pod.dict(skip_defaults=True), pod.dict(skip_defaults=True)
    ).to_string()
    response.response.patch = b64enc(patch)

    update_services(service, port, pod)
    return response


@app.get("/healthz/live")
async def liveness():
    return Response("{}", status_code=200)


@app.get("/healthz/ready")
async def readiness():
    return Response("{}", status_code=200)
