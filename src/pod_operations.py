from typing import List

import kubernetes_dynamic as kd

from kubernetes_client import get_client
from models import Config


def find_pods_services(
    pod: kd.models.V1Pod,
    port: kd.models.V1ContainerPort,
    kubernetes_client: kd.client.K8sClient = None,
) -> List[kd.models.V1Service]:
    _client = kubernetes_client or get_client()
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
                services = _client.services.find(
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
        kd.models.V1EnvVar(name=k, value=v)
        for k, v in {
            "OAUTH2_PROXY_PROVIDER": config.proxy_provider,
            "OAUTH2_PROXY_HTTP_ADDRESS": f"0.0.0.0:{config.proxy_http_port}",
            "OAUTH2_PROXY_REVERSE_PROXY": "true",
            "OAUTH2_PROXY_SKIP_PROVIDER_BUTTON": "true",
            "OAUTH2_PROXY_SESSION_COOKIE_MINIMAL": "true",
            "OAUTH2_PROXY_UPSTREAMS": f"http://127.0.0.1:{upstream_port_number}",
            "OAUTH2_PROXY_EMAIL_DOMAINS": config.proxy_email_domains,
            "OAUTH2_PROXY_ALLOWED_GROUPS": config.proxy_allowed_groups,
            "OAUTH2_PROXY_CLIENT_ID": config.proxy_client_id,
            "OAUTH2_PROXY_CLIENT_SECRET": config.proxy_client_secret,
            "OAUTH2_PROXY_REDIRECT_URL": config.proxy_redirect_url,
            "OAUTH2_PROXY_OIDC_ISSUER_URL": config.proxy_issuer_url,
            "OAUTH2_PROXY_COOKIE_NAME": config.proxy_cookie_name,
            "OAUTH2_PROXY_COOKIE_DOMAIN": config.proxy_cookie_domain,
            "OAUTH2_PROXY_COOKIE_SECRET": config.proxy_cookie_secret,
        }.items()
        if v
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
