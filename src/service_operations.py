from copy import deepcopy

import kubernetes_dynamic as kd
from kubernetes.client.exceptions import ApiException

from kubernetes_client import get_client
from utils import b64dec_json, b64enc_json

SERVICE_ANNOTATION_TYPE_KEY = "oauth2-proxy-admission/type"
SERVICE_ANNOTATION_TYPE_VALUE_SECURE = "secure"
SERVICE_ANNOTATION_TYPE_VALUE_INSECURE = "insecure"
SERVICE_ANNOTATION_POD_LABELS_KEY = "oauth2-proxy-admission/pod-labels"
SERVICE_ANNOTATION_PREVIOUS_VERSION = "oauth2-proxy-admission/previous-version"


def update_services(
    service: kd.models.V1Service,
    container_port: kd.models.V1ContainerPort,
    pod: kd.models.V1Pod,
    kubernetes_client: kd.client.K8sClient = None,
):
    _client = kubernetes_client or get_client()
    insecure_service = deepcopy(service)
    insecure_service.metadata.uid = None
    insecure_service.metadata.creationTimestamp = None
    insecure_service.metadata.managedFields = []
    insecure_service.metadata.resourceVersion = None
    insecure_service.spec.clusterIP = None
    insecure_service.spec.clusterIPs = None
    insecure_service.metadata.name = f"{service.metadata.name}-insecure"
    for sport in insecure_service.spec.ports:
        if (
            sport.targetPort == container_port.name
            or sport.targetPort == container_port.containerPort
        ):
            sport.targetPort = f"{sport.name}-insecure"
            break
    insecure_service.metadata.labels.update(
        {
            SERVICE_ANNOTATION_TYPE_KEY: SERVICE_ANNOTATION_TYPE_VALUE_INSECURE,
        }
    )
    insecure_service.metadata.annotations.update(
        {SERVICE_ANNOTATION_POD_LABELS_KEY: b64enc_json(pod.metadata.labels)}
    )
    try:
        _client.services.create(service.dict())
    except ApiException:
        _client.services.replace(insecure_service)


def revert_services(
    pod: kd.models.V1Pod, kubernetes_client: kd.client.K8sClient = None
):
    _client = kubernetes_client or get_client()
    services = _client.services.find(
        pattern=".*",
        namespace=pod.metadata.namespace,
        label_selector=f"{SERVICE_ANNOTATION_TYPE_KEY}={SERVICE_ANNOTATION_TYPE_VALUE_INSECURE}",
    )
    insecure_service = None
    for service in services:
        try:
            pod_labels_raw = service.metadata.annotations[
                SERVICE_ANNOTATION_POD_LABELS_KEY
            ]
            pod_labels = b64dec_json(pod_labels_raw)
            if pod.metadata.labels == pod_labels:
                insecure_service = service
        except KeyError:
            pass

    if insecure_service:
        _client.services.delete(
            insecure_service.metadata.name, insecure_service.metadata.namespace
        )
