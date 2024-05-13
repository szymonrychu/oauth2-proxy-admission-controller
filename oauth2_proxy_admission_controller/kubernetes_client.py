import logging

import kubernetes_dynamic as kd
from kubernetes import client, config

logger = logging.getLogger(__name__)


def get_client() -> kd.K8sClient:
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()
    _v1 = client.CoreV1Api()

    return kd.K8sClient(api_client=_v1.api_client)
