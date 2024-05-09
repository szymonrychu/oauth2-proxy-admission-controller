
from enum import Enum
from typing import Any, Dict, List
from uuid import UUID

import kubernetes_dynamic as kd
from pydantic import BaseModel, Field, create_model


class Config(BaseModel):
    proxy_container_name: str = Field(alias='proxy-container-name', default='proxy')
    proxy_provider: str = Field(alias='proxy-provider', default='keycloak-oidc')
    proxy_http_port: int = Field(alias='proxy-http-port', default=4180)
    proxy_email_domains: str = Field(alias='proxy-email-domains', default='*')
    proxy_allowed_groups: str = Field(alias='proxy-allowed-groups')
    proxy_client_id: str = Field(alias='proxy-client-id')
    proxy_client_secret: str = Field(alias='proxy-client-secret')
    proxy_redirect_url: str = Field(alias='proxy-redirect-url')
    proxy_issuer_url: str = Field(alias='proxy-oidc-issuer-url') # realm-url
    proxy_cookie_name: str = Field(alias='proxy-cookie-name')
    proxy_cookie_domain: str = Field(alias='proxy-cookie-domain')
    proxy_cookie_secret: str = Field(alias='proxy-cookie-secret')
    proxy_resources_requests_cpu: str = Field(alias='proxy-resources-requests-cpu', default='100m')
    proxy_resources_requests_memory: str = Field(alias='proxy-resources-requests-memory', default='128Mi')
    proxy_resources_limits_cpu: str = Field(alias='proxy-resources-limits-cpu', default='200m')
    proxy_resources_limits_memory: str = Field(alias='proxy-resources-limits-memory', default='256Mi')
    proxy_container_image: str = Field(alias='proxy-container-image', default='quay.io/oauth2-proxy/oauth2-proxy')
    proxy_container_tag: str = Field(alias='proxy-container-tag', default='v7.5.1')
    proxy_container_image_pull_policy: str = Field(alias='proxy-container-image-pull-policy', default='IfNotPresent')
    patch_container_name: str = Field(default=None)
    patch_port_number: int = Field(default=None)
    patch_port_name: str = Field(default=None)

class WebhookRequestOperation(Enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    CONNECT = 'CONNECT'

class V1AdmissionReviewRequestBody(BaseModel):
    # Random uid uniquely identifying this admission call
    uid: UUID
    # Name of the resource being modified
    name: str = None
    # Namespace of the resource being modified, if the resource is namespaced (or is a Namespace object)
    namespace: str = None
    # operation can be CREATE, UPDATE, DELETE, or CONNECT
    operation: WebhookRequestOperation
    # object is the new object being admitted.
    # It is null for DELETE operations.
    object: kd.models.V1Pod | None = Field(default=None)
    # oldObject is the existing object.
    # It is null for CREATE and CONNECT operations.
    old_object: kd.models.V1Pod | None = Field(alias='oldObject', default=None)
    # dryRun indicates the API request is running in dry run mode and will not be persisted.
    # Webhooks with side effects should avoid actuating those side effects when dryRun is true.
    # See http://k8s.io/docs/reference/using-api/api-concepts/#make-a-dry-run-request for more details.
    dry_run: bool = Field(alias='dryRun', default=False)

class V1AdmissionReviewRequest(kd.ResourceItem):
    api_version: str = Field(alias='apiVersion', default='admission.k8s.io/v1')
    kind: str = 'AdmissionReview'
    request: V1AdmissionReviewRequestBody

class V1AdmissionReviewResponseBody(BaseModel):
    uid: UUID
    allowed: bool = True
    patch: str | None = None
    patch_type: str | None = Field(alias='patchType', default=None)

class V1AdmissionReviewResponse(kd.ResourceItem):
    api_version: str = Field(alias='apiVersion', default='admission.k8s.io/v1')
    kind: str = 'AdmissionReview'
    response: V1AdmissionReviewResponseBody


def get_admission_resp_from_req(req:V1AdmissionReviewRequest, allowed:bool= True, patch:str = None, patch_type:str = None) -> V1AdmissionReviewResponse:
    response = V1AdmissionReviewResponseBody(uid=req.request.uid, allowed=allowed, patch=patch, patch_type=patch_type)
    resp = V1AdmissionReviewResponse(response = response, kind = req.kind, api_version = req.api_version)
    return resp

