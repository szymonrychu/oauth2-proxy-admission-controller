
from pydantic import BaseModel, Field, create_model
from typing import Any, List, Dict
from uuid import UUID
from enum import Enum

class KubernetesObject(BaseModel):
    api_version: str = Field(alias='apiVersion')
    kind: str
    metadata: Dict[str, Any]
    spec: Dict[str, Any]

class WebhookRequestResourceDetails(BaseModel):
    group: str
    version: str
    kind: str

class WebhookRequestOperation(Enum):
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    CONNECT = 'CONNECT'

class WebhookRequestUserInfo(BaseModel):
    # Username of the authenticated user making the request to the API server
    username: str
    # UID of the authenticated user making the request to the API server
    uid: UUID
    # Group memberships of the authenticated user making the request to the API server
    groups: List[str]
    # Arbitrary extra info associated with the user making the request to the API server.
    # This is populated by the API server authentication layer and should be included
    # if any SubjectAccessReview checks are performed by the webhook.
    extra: Dict[str, List[str]]

class WebhookRequestBody(BaseModel):
    # Random uid uniquely identifying this admission call
    uid: UUID
    # Fully-qualified group/version/kind of the incoming object
    kind: WebhookRequestResourceDetails
    # Fully-qualified group/version/kind of the resource being modified
    resource: WebhookRequestResourceDetails
    # subresource, if the request is to a subresource
    sub_resource: str = Field(alias='subResource')
    # Fully-qualified group/version/kind of the incoming object in the original request to the API server.
    # This only differs from `kind` if the webhook specified `matchPolicy: Equivalent` and the
    # original request to the API server was converted to a version the webhook registered for.
    request_kind: WebhookRequestResourceDetails = Field(alias='requestKind')
    # Fully-qualified group/version/kind of the resource being modified in the original request to the API server.
    # This only differs from `resource` if the webhook specified `matchPolicy: Equivalent` and the
    # original request to the API server was converted to a version the webhook registered for.
    request_resource: WebhookRequestResourceDetails = Field(alias='requestResource')
    # subresource, if the request is to a subresource
    # This only differs from `subResource` if the webhook specified `matchPolicy: Equivalent` and the
    # original request to the API server was converted to a version the webhook registered for.
    request_sub_resource: str = Field(alias='requestSubResource')
    # Name of the resource being modified
    name: str
    # Namespace of the resource being modified, if the resource is namespaced (or is a Namespace object)
    namespace: str
    # operation can be CREATE, UPDATE, DELETE, or CONNECT
    operation: WebhookRequestOperation
    user_info: WebhookRequestUserInfo = Field(alias='userInfo')
    # object is the new object being admitted.
    # It is null for DELETE operations.
    object: KubernetesObject = Field(default=None)
    # oldObject is the existing object.
    # It is null for CREATE and CONNECT operations.
    old_object: KubernetesObject = Field(alias='oldObject', default=None)
    # options contains the options for the operation being admitted, like meta.k8s.io/v1 CreateOptions, UpdateOptions, or DeleteOptions.
    # It is null for CONNECT operations.
    options: KubernetesObject = Field(default=None)
    # dryRun indicates the API request is running in dry run mode and will not be persisted.
    # Webhooks with side effects should avoid actuating those side effects when dryRun is true.
    # See http://k8s.io/docs/reference/using-api/api-concepts/#make-a-dry-run-request for more details.
    dry_run: bool = Field(alias='dryRun', default=False)

class WebhookRequest(BaseModel):
    api_version: str = Field(alias='apiVersion')
    kind: str
    request: WebhookRequestBody

class WebhookResponseBodyStatus(BaseModel):
    code: int
    message: str

class WebhookResponseBody(BaseModel):
    uid: UUID = UUID('{12345678-1234-5678-1234-567812345678}')
    allowed: bool = True
    status: WebhookResponseBodyStatus = None
    patch: str = None
    patch_type: str = Field(alias='patchType', default=None)
    warnings: List[str] = None


class WebhookResponse(BaseModel):
    api_version: str = Field(alias='apiVersion', default='')
    kind: str = ''
    response: WebhookResponseBody = WebhookResponseBody()
    



'''
apiVersion: v1
kind: Pod
metadata:
  annotations:
    prometheus.io/path: /metrics
    prometheus.io/port: "9402"
    prometheus.io/scrape: "true"
  creationTimestamp: "2024-03-06T21:12:30Z"
  generateName: cert-manager-86749699db-
  labels:
    allow: "yes"
    app: cert-manager
    app.kubernetes.io/component: controller
    app.kubernetes.io/instance: cert-manager
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: cert-manager
    app.kubernetes.io/version: v1.14.3
    helm.sh/chart: cert-manager-v1.14.3
    pod-template-hash: 86749699db
  name: cert-manager-86749699db-g9lmx
  namespace: ingress-system
  ownerReferences:
  - apiVersion: apps/v1
    blockOwnerDeletion: true
    controller: true
    kind: ReplicaSet
    name: cert-manager-86749699db
    uid: 75607af6-c272-4e43-8e91-8944241d9a8e
  resourceVersion: "35621988"
  uid: f8597f1f-d1b8-482f-99ce-024cf0b5525c
spec:
  containers:
  - args:
    - --v=2
    - --cluster-resource-namespace=$(POD_NAMESPACE)
    - --leader-election-namespace=kube-system
    - --acme-http01-solver-image=quay.io/jetstack/cert-manager-acmesolver:v1.14.3
    - --max-concurrent-challenges=60
    env:
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          apiVersion: v1
          fieldPath: metadata.namespace
    image: quay.io/jetstack/cert-manager-controller:v1.14.3
    imagePullPolicy: IfNotPresent
    livenessProbe:
      failureThreshold: 8
      httpGet:
        path: /livez
        port: http-healthz
        scheme: HTTP
      initialDelaySeconds: 10
      periodSeconds: 10
      successThreshold: 1
      timeoutSeconds: 15
    name: cert-manager-controller
    ports:
    - containerPort: 9402
      name: http-metrics
      protocol: TCP
    - containerPort: 9403
      name: http-healthz
      protocol: TCP
    resources:
      limits:
        cpu: 100m
        memory: 96Mi
      requests:
        cpu: 10m
        memory: 32Mi
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
    terminationMessagePath: /dev/termination-log
    terminationMessagePolicy: File
    volumeMounts:
    - mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      name: kube-api-access-jqn2s
      readOnly: true
  dnsPolicy: ClusterFirst
  enableServiceLinks: false
  nodeName: nuc1
  nodeSelector:
    kubernetes.io/os: linux
  preemptionPolicy: PreemptLowerPriority
  priority: 0
  restartPolicy: Always
  schedulerName: default-scheduler
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  serviceAccount: cert-manager
  serviceAccountName: cert-manager
  terminationGracePeriodSeconds: 30
  tolerations:
  - effect: NoExecute
    key: node.kubernetes.io/not-ready
    operator: Exists
    tolerationSeconds: 300
  - effect: NoExecute
    key: node.kubernetes.io/unreachable
    operator: Exists
    tolerationSeconds: 300
  volumes:
  - name: kube-api-access-jqn2s
    projected:
      defaultMode: 420
      sources:
      - serviceAccountToken:
          expirationSeconds: 3607
          path: token
      - configMap:
          items:
          - key: ca.crt
            path: ca.crt
          name: kube-root-ca.crt
      - downwardAPI:
          items:
          - fieldRef:
              apiVersion: v1
              fieldPath: metadata.namespace
            path: namespace
status:
  conditions:
  - lastProbeTime: null
    lastTransitionTime: "2024-03-06T21:12:31Z"
    status: "True"
    type: Initialized
  - lastProbeTime: null
    lastTransitionTime: "2024-03-06T21:12:33Z"
    status: "True"
    type: Ready
  - lastProbeTime: null
    lastTransitionTime: "2024-03-06T21:12:33Z"
    status: "True"
    type: ContainersReady
  - lastProbeTime: null
    lastTransitionTime: "2024-03-06T21:12:31Z"
    status: "True"
    type: PodScheduled
  containerStatuses:
  - containerID: containerd://5c095d258543d63e2e98ad31f5f61cb39b98e2d9999505ecef2f47d93e650945
    image: quay.io/jetstack/cert-manager-controller:v1.14.3
    imageID: quay.io/jetstack/cert-manager-controller@sha256:64adcb95ce09efcc4c42c1a42633ef141d15b83b25efbd6264912ba24b77023f
    lastState: {}
    name: cert-manager-controller
    ready: true
    restartCount: 0
    started: true
    state:
      running:
        startedAt: "2024-03-06T21:12:32Z"
  hostIP: 192.168.1.65
  phase: Running
  podIP: 10.244.0.224
  podIPs:
  - ip: 10.244.0.224
  qosClass: Burstable
  startTime: "2024-03-06T21:12:31Z"
'''