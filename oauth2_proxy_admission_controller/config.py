import logging
import os
from typing import Optional

import kubernetes_dynamic as kd
from kubernetes.client.exceptions import ApiException

from oauth2_proxy_admission_controller.kubernetes_client import get_client
from oauth2_proxy_admission_controller.models import Config
from oauth2_proxy_admission_controller.utils import b64dec

logger = logging.getLogger(__name__)

POD_ANNOTATIONS_PREFIX = "oauth2-proxy-admission/"

DEFAULT_SECRET_NAME = "OAUTH2_PROXY_ADMISSION_SECRET_NAME"
DEFAULT_SECRET_NAMESPACE = "OAUTH2_PROXY_ADMISSION_SECRET_NAMESPACE"

_default_secret_name = os.environ.get(DEFAULT_SECRET_NAME, None)
_default_secret_namespace = os.environ.get(DEFAULT_SECRET_NAMESPACE, None)


def load_from_kubernetes(
    secret_name: str = None, secret_namespace: str = None, kubernetes_client: kd.client.K8sClient = None
) -> Optional[Config]:
    _client = kubernetes_client or get_client()
    if not secret_name:
        return None
    try:
        config_raw = _client.secrets.get(secret_name, secret_namespace).data
        return Config.validate({k: b64dec(v) for k, v in config_raw.items()})
    except ApiException:
        return None


def load_from_annotations(pod: kd.models.V1Pod) -> Config:
    result = {}
    prefix_len = len(POD_ANNOTATIONS_PREFIX)
    for k, v in pod.metadata.annotations.items():
        if k.startswith(POD_ANNOTATIONS_PREFIX):
            result[k[prefix_len:]] = v
    return Config.validate(result)


def load_config(pod: kd.models.V1Pod, kubernetes_client: kd.client.K8sClient = None) -> Optional[Config]:
    annotations_config = load_from_annotations(pod)

    config = Config()

    if _default_secret_name:
        config_update = load_from_kubernetes(_default_secret_name, _default_secret_namespace, kubernetes_client)
        if config_update:
            config.update(config_update)
        else:
            logger.warning("Default configuration secret name and namespace not provided!")
    else:
        logger.warning("Configuration default secret name not provided!")

    if annotations_config.secret_name:
        config_update = load_from_kubernetes(
            annotations_config.secret_name, annotations_config.secret_namespace, kubernetes_client
        )
        if config_update:
            config.update(config_update)
        else:
            logger.warning("Configuration secret name and namespace not provided!")
    else:
        logger.warning("Configuration secret name not provided!")

    config = config.update(annotations_config)

    if config.all_required_fields_set:
        return config
    else:
        logger.warning(f"Configuration not provided, missing fields: [{', '.join(config.missing_fields)}]")
        return None
