import logging
from copy import deepcopy

import jsonpatch
from fastapi import FastAPI, Response

from oauth2_proxy_admission_controller.config import load_config
from oauth2_proxy_admission_controller.models import (
    V1AdmissionReviewRequest,
    V1AdmissionReviewResponse,
    get_admission_resp_from_req,
)
from oauth2_proxy_admission_controller.pod_operations import (
    find_pods_services,
    generate_proxy_container,
    get_container_port,
    get_pod_container,
)
from oauth2_proxy_admission_controller.service_operations import (
    revert_services,
    update_services,
)
from oauth2_proxy_admission_controller.utils import b64enc

logger = logging.getLogger(__name__)

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

    logger.info(f"Handling {pod.metadata.namespace}/{pod.metadata.name}")
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
    pod.spec.containers.append(generate_proxy_container(port.containerPort, port.name, config))

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

    update_services(service, port, pod)

    port.name = f"{port.name}-insecure"
    response.response.patch_type = "JSONPatch"
    patch = jsonpatch.make_patch(old_pod.dict(skip_defaults=True), pod.dict(skip_defaults=True)).to_string()
    response.response.patch = b64enc(patch)

    return response


@app.get("/healthz/live")
async def liveness():
    return Response("{}", status_code=200)


@app.get("/healthz/ready")
async def readiness():
    return Response("{}", status_code=200)
