from copy import deepcopy
from typing import List, Optional

import kubernetes_dynamic as kd

from models import Config


def patch_pod(pod:kd.models.V1Pod, config:Config) -> kd.models.V1Pod:
    patched_pod = deepcopy(pod)

    container = None
    for c in patched_pod.spec.containers:
        if not config.patch_container_name or c.name == config.patch_container_name:
            container = c
            break
    if not container:
        return pod
    
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
    if not port:
        return pod

    port.name = f"{port.name}-unsecured"

    new_container = kd.models.V1Container()
    new_container.name = config.proxy_container_name
    new_container.image = f"{config.proxy_container_image}:{config.proxy_container_tag}"
    new_container.imagePullPolicy = config.proxy_container_image_pull_policy
    new_container.env = [
        kd.models.V1EnvVar(name='OAUTH2_PROXY_PROVIDER', value=config.proxy_provider),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_HTTP_ADDRESS', value=f"0.0.0.0:{config.proxy_http_port}"),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_REVERSE_PROXY', value='true'),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_SKIP_PROVIDER_BUTTON', value='true'),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_UPSTREAMS', value=f"http://127.0.0.1:{port.containerPort}"),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_SESSION_COOKIE_MINIMAL', value='true'),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_EMAIL_DOMAINS', value=config.proxy_email_domains),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_ALLOWED_GROUPS', value=config.proxy_allowed_groups),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_CLIENT_ID', value=config.proxy_client_id),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_CLIENT_SECRET', value=config.proxy_client_secret),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_REDIRECT_URL', value=config.proxy_redirect_url),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_OIDC_ISSUER_URL', value=config.proxy_issuer_url),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_COOKIE_NAME', value=config.proxy_cookie_name),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_COOKIE_DOMAIN', value=config.proxy_cookie_domain),
        kd.models.V1EnvVar(name='OAUTH2_PROXY_COOKIE_SECRET', value=config.proxy_cookie_secret),
    ]
    new_container.ports = [
        kd.models.V1ContainerPort(containerPort=config.proxy_http_port, name=port.name)
    ]
    new_container.livenessProbe = kd.models.V1Probe(failureThreshold=3, periodSeconds=10, successThreshold=1, tcpSocket=kd.models.V1TCPSocketAction(port=port.name))
    new_container.readinessProbe = kd.models.V1Probe(failureThreshold=3, periodSeconds=10, successThreshold=1, tcpSocket=kd.models.V1TCPSocketAction(port=port.name))
    new_container.resources = kd.models.V1ResourceRequirements(limits = {
        'cpu': config.proxy_resources_limits_cpu,
        'memory': config.proxy_resources_limits_memory,
    }, requests = {
        'cpu': config.proxy_resources_requests_cpu,
        'memory': config.proxy_resources_requests_memory,
    })

    patched_pod.spec.containers.append(new_container)

    return patched_pod

