
from pydantic import BaseModel, Field, create_model
from typing import Any, List, Dict
from uuid import UUID
from enum import Enum

class ConfiguredBasedModel(BaseModel):

    class Config:
        # alias_generator = to_camel
        populate_by_name = True

class KubernetesObject(ConfiguredBasedModel):
    api_version: str = Field(alias='apiVersion')
    kind: str
    metadata: Any
    spec: Any

class WebhookRequestResourceDetails(ConfiguredBasedModel):
    group: str
    version: str
    kind: str

class WebhookRequestOperation(Enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    CONNECT = 'CONNECT'

class WebhookRequestBody(ConfiguredBasedModel):
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
    object: KubernetesObject | None = Field(default=None)
    # oldObject is the existing object.
    # It is null for CREATE and CONNECT operations.
    old_object: KubernetesObject | None = Field(alias='oldObject', default=None)
    # dryRun indicates the API request is running in dry run mode and will not be persisted.
    # Webhooks with side effects should avoid actuating those side effects when dryRun is true.
    # See http://k8s.io/docs/reference/using-api/api-concepts/#make-a-dry-run-request for more details.
    dry_run: bool = Field(alias='dryRun', default=False)

class WebhookRequest(ConfiguredBasedModel):
    api_version: str = Field(alias='apiVersion')
    kind: str
    request: WebhookRequestBody

class WebhookResponseBodyStatus(ConfiguredBasedModel):
    code: int
    message: str

class WebhookResponseBody(ConfiguredBasedModel):
    uid: UUID = UUID('{12345678-1234-5678-1234-567812345678}')
    allowed: bool = True
    status: dict = {}
    patch: str = 'W10='
    patch_type: str = Field(alias='patchType', default='JSONPatch')
    warnings: List[str] = []


class WebhookResponse(ConfiguredBasedModel):
    api_version: str = Field(alias='apiVersion', default='admission.k8s.io/v1')
    kind: str = 'AdmissionReview'
    response: WebhookResponseBody = WebhookResponseBody()
    
