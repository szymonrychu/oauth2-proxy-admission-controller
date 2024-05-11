import base64
import json
import os
from copy import deepcopy
from typing import Any, List, Optional
import kubernetes_dynamic as kd
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from models import Config

try:
    config.load_incluster_config()
except Exception:
    config.load_kube_config()
_v1 = client.CoreV1Api()
_kd_client = kd.K8sClient(api_client=_v1.api_client)

SERVICE_ANNOTATION_TYPE_KEY = "oauth2-proxy-admission/type"
SERVICE_ANNOTATION_TYPE_VALUE_SECURE = "secure"
SERVICE_ANNOTATION_TYPE_VALUE_INSECURE = "insecure"
SERVICE_ANNOTATION_POD_LABELS_KEY = "oauth2-proxy-admission/pod-labels"
SERVICE_ANNOTATION_PREVIOUS_VERSION = "oauth2-proxy-admission/previous-version"


def b64dec(data: str) -> str:
    return base64.b64decode(data.encode("utf-8")).decode("utf-8")


def b64enc(data: str) -> str:
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def b64dec_json(data: str) -> Any:
    return b64dec(json.dumps(data))


def b64enc_json(data: Any) -> str:
    return json.loads(b64enc(data))


def get_config(
    secret_name: str = None, secret_namespace: str = None
) -> Optional[Config]:
    default_config_secret_name = os.environ.get(
        "OAUTH2_PROXY_ADMISSION_SECRET_NAME", None
    )
    default_config_secret_namespace = os.environ.get(
        "OAUTH2_PROXY_ADMISSION_SECRET_NAMESPACE", None
    )

    raw_configuration = {}
    if default_config_secret_name:
        raw_configuration = _kd_client.secrets.get(
            default_config_secret_name, default_config_secret_namespace
        ).data

    raw_overrides = {}
    if secret_name:
        raw_overrides = _kd_client.secrets.get(secret_name, secret_namespace).data

    for k, v in raw_overrides.items():
        raw_configuration[k] = v

    result = {}
    for k, v in raw_configuration.items():
        result[k] = base64.b64decode(v).decode("ascii")

    return Config.validate(result)


def get_pod_container(pod: kd.models.V1Pod, config: Config) -> kd.models.V1Container:
    container = None
    for c in pod.spec.containers:
        if not config.patch_container_name or c.name == config.patch_container_name:
            container = c
            break
    return container


def get_container_port(
    container: kd.models.V1Container, config: Config
) -> kd.models.V1ContainerPort:
    port = None
    for p in container.ports:
        if not config.patch_port_name and not config.patch_port_number:
            port = p
            break
        elif config.patch_port_name and config.patch_port_name == p.name:
            port = p
            break
        elif config.patch_port_number and config.patch_port_number == p.containerPort:
            port = p
            break
    return port


def generate_proxy_container(
    upstream_port_number: int, port_name: str, config: Config
) -> kd.models.V1Container:
    new_container = kd.models.V1Container()
    new_container.name = config.proxy_container_name
    new_container.image = f"{config.proxy_container_image}:{config.proxy_container_tag}"
    new_container.imagePullPolicy = config.proxy_container_image_pull_policy
    new_container.env = [
        kd.models.V1EnvVar(name="OAUTH2_PROXY_PROVIDER", value=config.proxy_provider),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_HTTP_ADDRESS", value=f"0.0.0.0:{config.proxy_http_port}"
        ),
        kd.models.V1EnvVar(name="OAUTH2_PROXY_REVERSE_PROXY", value="true"),
        kd.models.V1EnvVar(name="OAUTH2_PROXY_SKIP_PROVIDER_BUTTON", value="true"),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_UPSTREAMS",
            value=f"http://127.0.0.1:{upstream_port_number}",
        ),
        kd.models.V1EnvVar(name="OAUTH2_PROXY_SESSION_COOKIE_MINIMAL", value="true"),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_EMAIL_DOMAINS", value=config.proxy_email_domains
        ),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_ALLOWED_GROUPS", value=config.proxy_allowed_groups
        ),
        kd.models.V1EnvVar(name="OAUTH2_PROXY_CLIENT_ID", value=config.proxy_client_id),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_CLIENT_SECRET", value=config.proxy_client_secret
        ),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_REDIRECT_URL", value=config.proxy_redirect_url
        ),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_OIDC_ISSUER_URL", value=config.proxy_issuer_url
        ),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_COOKIE_NAME", value=config.proxy_cookie_name
        ),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_COOKIE_DOMAIN", value=config.proxy_cookie_domain
        ),
        kd.models.V1EnvVar(
            name="OAUTH2_PROXY_COOKIE_SECRET", value=config.proxy_cookie_secret
        ),
    ]
    new_container.ports = [
        kd.models.V1ContainerPort(containerPort=config.proxy_http_port, name=port_name)
    ]
    new_container.livenessProbe = kd.models.V1Probe(
        failureThreshold=3,
        periodSeconds=10,
        successThreshold=1,
        tcpSocket=kd.models.V1TCPSocketAction(port=port_name),
    )
    new_container.readinessProbe = kd.models.V1Probe(
        failureThreshold=3,
        periodSeconds=10,
        successThreshold=1,
        tcpSocket=kd.models.V1TCPSocketAction(port=port_name),
    )
    new_container.resources = kd.models.V1ResourceRequirements(
        limits={
            "cpu": config.proxy_resources_limits_cpu,
            "memory": config.proxy_resources_limits_memory,
        },
        requests={
            "cpu": config.proxy_resources_requests_cpu,
            "memory": config.proxy_resources_requests_memory,
        },
    )
    return new_container


def find_pods_services(
    pod: kd.models.V1Pod, port: kd.models.V1ContainerPort
) -> List[kd.models.V1Service]:
    labels = pod.metadata.labels
    labels_keys = list(labels.keys())
    labels_num = len(labels_keys)
    for starting_point in range(labels_num):
        selector = {}
        for b in range(labels_num):
            k = labels_keys[(starting_point + b) % labels_num]
            selector[k] = labels[k]

        for c in range(labels_num):
            if selector:
                _selector = []
                for k, v in selector.items():
                    _selector.append(f"{k}={v}")
                _full_selector = ",".join(_selector)
                services = _kd_client.services.find(
                    pattern=".*",
                    namespace=pod.metadata.namespace,
                    label_selector=_full_selector,
                )
                for service in services:
                    for sport in service.spec.ports:
                        if port.name and port.name == sport.targetPort:
                            return service
                        elif port.containerPort == sport.targetPort:
                            return service
            del selector[labels_keys[labels_num - c - 1]]
    return []


def delete_service(service: kd.models.V1Service):
    _kd_client.services.delete(service.metadata.name, service.metadata.namespace)


def _upsert_service(service: kd.models.V1Service) -> kd.models.V1Service:
    return _kd_client.services.replace(service.dict())


def update_services(
    service: kd.models.V1Service,
    container_port: kd.models.V1ContainerPort,
    pod: kd.models.V1Pod,
):
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
        {SERVICE_ANNOTATION_POD_LABELS_KEY: b64enc(json.dumps(pod.metadata.labels))}
    )
    try:
        _kd_client.services.create(service.dict())
    except ApiException:
        _kd_client.services.replace(insecure_service)


def revert_services(pod: kd.models.V1Pod):
    services = _kd_client.services.find(
        pattern=".*",
        namespace=pod.metadata.namespace,
        label_selector=f"{SERVICE_ANNOTATION_TYPE_KEY}={SERVICE_ANNOTATION_TYPE_VALUE_INSECURE}",
    )
    insecure_service = None
    for service in services:
        if SERVICE_ANNOTATION_POD_LABELS_KEY in service.metadata.annotations:
            pod_labels_raw = service.metadata.annotations[
                SERVICE_ANNOTATION_POD_LABELS_KEY
            ]
            pod_labels_string = b64dec(pod_labels_raw)
            if json.dumps(pod.metadata.labels) == pod_labels_string:
                insecure_service = service

    if insecure_service:
        _kd_client.services.delete(
            insecure_service.metadata.name, insecure_service.metadata.namespace
        )
