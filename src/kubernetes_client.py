import kubernetes_dynamic as kd
from kubernetes import client, config

try:
    config.load_incluster_config()
except Exception:
    config.load_kube_config()
_v1 = client.CoreV1Api()

client = kd.K8sClient(api_client=_v1.api_client)
