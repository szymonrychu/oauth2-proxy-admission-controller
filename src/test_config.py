import kubernetes_dynamic as kd
from kubernetes.client.exceptions import ApiException

from utils import b64enc
from config import load_config, load_from_annotations, load_from_kubernetes


class MockSecrets:
    def get(self, secret_name: str, secret_namespace: str = None) -> kd.models.V1Secret:
        if secret_name == "non_existent":
            raise ApiException()
        secret = kd.models.V1Secret()
        secret.metadata.name = secret_name
        secret.metadata.namespace = secret_namespace or "default"
        secret.data["proxy-container-name"] = b64enc("test_secret")
        secret.data["proxy-provider"] = b64enc("test_secret")
        secret.data["proxy-http-port"] = b64enc(str(123))
        secret.data["proxy-email-domains"] = b64enc("test_secret")
        secret.data["proxy-allowed-groups"] = b64enc("test_secret")
        secret.data["proxy-client-id"] = b64enc("test_secret")
        secret.data["proxy-client-secret"] = b64enc("test_secret")
        if secret_name != "test_missing_fields":
            secret.data["proxy-redirect-url"] = b64enc("test_secret")
            secret.data["proxy-oidc-issuer-url"] = b64enc("test_secret")
            secret.data["proxy-cookie-name"] = b64enc("test_secret")
            secret.data["proxy-cookie-domain"] = b64enc("test_secret")
        secret.data["proxy-cookie-secret"] = b64enc("test_secret")
        secret.data["proxy-resources-requests-cpu"] = b64enc("test_secret")
        secret.data["proxy-resources-requests-memory"] = b64enc("test_secret")
        secret.data["proxy-resources-limits-cpu"] = b64enc("test_secret")
        secret.data["proxy-resources-limits-memory"] = b64enc("test_secret")
        secret.data["proxy-container-image"] = b64enc("test_secret")
        secret.data["proxy-container-tag"] = b64enc("test_secret")
        secret.data["proxy-container-image-pull-policy"] = b64enc("test_secret")
        secret.data["patch-container-name"] = b64enc("test_secret")
        secret.data["patch-port-number"] = b64enc(str(123))
        secret.data["proxy-port-name"] = b64enc("test_secret")
        secret.data["secret-name"] = b64enc("test_secret")
        secret.data["secret-namespace"] = b64enc("test_secret")
        return secret


class MockClient:
    def __init__(self):
        self.secrets = MockSecrets()


def test_load_from_kubernetes_name_empty():
    mock_client = MockClient()

    config = load_from_kubernetes(None, None, mock_client)
    assert config is None


def test_load_from_kubernetes_secret_not_exists():
    mock_client = MockClient()

    config = load_from_kubernetes("non_existent", None, mock_client)
    assert config is None


def test_load_from_kubernetes_secret_missing_fields():
    mock_client = MockClient()

    config = load_from_kubernetes("test_missing_fields", "test", mock_client)
    assert not config.all_required_fields_set


def test_load_from_kubernetes():
    mock_client = MockClient()

    config = load_from_kubernetes("test", "test", mock_client)

    assert config is not None
    assert config.proxy_container_name == "test_secret"
    assert config.proxy_provider == "test_secret"
    assert config.proxy_http_port == 123
    assert config.proxy_email_domains == "test_secret"
    assert config.proxy_allowed_groups == "test_secret"
    assert config.proxy_client_id == "test_secret"
    assert config.proxy_client_secret == "test_secret"
    assert config.proxy_redirect_url == "test_secret"
    assert config.proxy_issuer_url == "test_secret"
    assert config.proxy_cookie_name == "test_secret"
    assert config.proxy_cookie_domain == "test_secret"
    assert config.proxy_cookie_secret == "test_secret"
    assert config.proxy_resources_requests_cpu == "test_secret"
    assert config.proxy_resources_requests_memory == "test_secret"
    assert config.proxy_resources_limits_cpu == "test_secret"
    assert config.proxy_resources_limits_memory == "test_secret"
    assert config.proxy_container_image == "test_secret"
    assert config.proxy_container_tag == "test_secret"
    assert config.proxy_container_image_pull_policy == "test_secret"
    assert config.patch_container_name == "test_secret"
    assert config.patch_port_number == 123
    assert config.patch_port_name == "test_secret"
    assert config.secret_name == "test_secret"
    assert config.secret_namespace == "test_secret"
    assert config.all_required_fields_set


def test_load_from_annotations():
    test_pod = kd.models.V1Pod()
    test_pod.metadata.annotations = {
        "oauth2-proxy-admission/proxy-container-name": "test_pod",
        "oauth2-proxy-admission/proxy-provider": "test_pod",
        "oauth2-proxy-admission/proxy-http-port": str(123),
        "oauth2-proxy-admission/proxy-email-domains": "test_pod",
        "oauth2-proxy-admission/proxy-allowed-groups": "test_pod",
        "oauth2-proxy-admission/proxy-client-id": "test_pod",
        "oauth2-proxy-admission/proxy-client-secret": "test_pod",
        "oauth2-proxy-admission/proxy-redirect-url": "test_pod",
        "oauth2-proxy-admission/proxy-oidc-issuer-url": "test_pod",
        "oauth2-proxy-admission/proxy-cookie-name": "test_pod",
        "oauth2-proxy-admission/proxy-cookie-domain": "test_pod",
        "oauth2-proxy-admission/proxy-cookie-secret": "test_pod",
        "oauth2-proxy-admission/proxy-resources-requests-cpu": "test_pod",
        "oauth2-proxy-admission/proxy-resources-requests-memory": "test_pod",
        "oauth2-proxy-admission/proxy-resources-limits-cpu": "test_pod",
        "oauth2-proxy-admission/proxy-resources-limits-memory": "test_pod",
        "oauth2-proxy-admission/proxy-container-image": "test_pod",
        "oauth2-proxy-admission/proxy-container-tag": "test_pod",
        "oauth2-proxy-admission/proxy-container-image-pull-policy": "test_pod",
        "oauth2-proxy-admission/patch-container-name": "test_pod",
        "oauth2-proxy-admission/patch-port-number": str(123),
        "oauth2-proxy-admission/proxy-port-name": "test_pod",
        "oauth2-proxy-admission/secret-name": "test_pod",
        "oauth2-proxy-admission/secret-namespace": "test_pod",
    }

    config = load_from_annotations(test_pod)

    assert config is not None
    assert config.proxy_container_name == "test_pod"
    assert config.proxy_provider == "test_pod"
    assert config.proxy_http_port == 123
    assert config.proxy_email_domains == "test_pod"
    assert config.proxy_allowed_groups == "test_pod"
    assert config.proxy_client_id == "test_pod"
    assert config.proxy_client_secret == "test_pod"
    assert config.proxy_redirect_url == "test_pod"
    assert config.proxy_issuer_url == "test_pod"
    assert config.proxy_cookie_name == "test_pod"
    assert config.proxy_cookie_domain == "test_pod"
    assert config.proxy_cookie_secret == "test_pod"
    assert config.proxy_resources_requests_cpu == "test_pod"
    assert config.proxy_resources_requests_memory == "test_pod"
    assert config.proxy_resources_limits_cpu == "test_pod"
    assert config.proxy_resources_limits_memory == "test_pod"
    assert config.proxy_container_image == "test_pod"
    assert config.proxy_container_tag == "test_pod"
    assert config.proxy_container_image_pull_policy == "test_pod"
    assert config.patch_container_name == "test_pod"
    assert config.patch_port_number == 123
    assert config.patch_port_name == "test_pod"
    assert config.secret_name == "test_pod"
    assert config.secret_namespace == "test_pod"
    assert config.all_required_fields_set


def test_load_config():
    test_pod = kd.models.V1Pod()
    test_pod.metadata.annotations = {
        "oauth2-proxy-admission/proxy-container-name": "test_pod",
        "oauth2-proxy-admission/proxy-provider": "test_pod",
        "oauth2-proxy-admission/proxy-http-port": str(456),
        "oauth2-proxy-admission/proxy-email-domains": "test_pod",
        "oauth2-proxy-admission/proxy-allowed-groups": "test_pod",
        "oauth2-proxy-admission/proxy-client-id": "test_pod",
        "oauth2-proxy-admission/proxy-client-secret": "test_pod",
        "oauth2-proxy-admission/proxy-redirect-url": "test_pod",
        "oauth2-proxy-admission/proxy-oidc-issuer-url": "test_pod",
        "oauth2-proxy-admission/proxy-cookie-name": "test_pod",
        "oauth2-proxy-admission/proxy-cookie-domain": "test_pod",
        "oauth2-proxy-admission/proxy-cookie-secret": "test_pod",
        "oauth2-proxy-admission/proxy-resources-requests-cpu": "test_pod",
        "oauth2-proxy-admission/proxy-resources-requests-memory": "test_pod",
        "oauth2-proxy-admission/proxy-resources-limits-cpu": "test_pod",
        "oauth2-proxy-admission/proxy-resources-limits-memory": "test_pod",
        "oauth2-proxy-admission/proxy-container-image": "test_pod",
        "oauth2-proxy-admission/proxy-container-tag": "test_pod",
        "oauth2-proxy-admission/proxy-container-image-pull-policy": "test_pod",
        "oauth2-proxy-admission/patch-container-name": "test_pod",
        "oauth2-proxy-admission/patch-port-number": str(456),
        "oauth2-proxy-admission/proxy-port-name": "test_pod",
        "oauth2-proxy-admission/secret-name": "test_pod",
        "oauth2-proxy-admission/secret-namespace": "test_pod",
    }
    mock_client = MockClient()

    config = load_config(test_pod, mock_client)

    assert config is not None
    assert config.proxy_container_name == "test_pod"
    assert config.proxy_provider == "test_pod"
    assert config.proxy_http_port == 456
    assert config.proxy_email_domains == "test_pod"
    assert config.proxy_allowed_groups == "test_pod"
    assert config.proxy_client_id == "test_pod"
    assert config.proxy_client_secret == "test_pod"
    assert config.proxy_redirect_url == "test_pod"
    assert config.proxy_issuer_url == "test_pod"
    assert config.proxy_cookie_name == "test_pod"
    assert config.proxy_cookie_domain == "test_pod"
    assert config.proxy_cookie_secret == "test_pod"
    assert config.proxy_resources_requests_cpu == "test_pod"
    assert config.proxy_resources_requests_memory == "test_pod"
    assert config.proxy_resources_limits_cpu == "test_pod"
    assert config.proxy_resources_limits_memory == "test_pod"
    assert config.proxy_container_image == "test_pod"
    assert config.proxy_container_tag == "test_pod"
    assert config.proxy_container_image_pull_policy == "test_pod"
    assert config.patch_container_name == "test_pod"
    assert config.patch_port_number == 456
    assert config.patch_port_name == "test_pod"
    assert config.secret_name == "test_pod"
    assert config.secret_namespace == "test_pod"
    assert config.all_required_fields_set
