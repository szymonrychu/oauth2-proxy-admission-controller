import base64
import os
from typing import Optional

import kubernetes_dynamic as kd
from pydantic.error_wrappers import ValidationError

from models import Config


def get_config(secret_name:str = None, secret_namespace:str = None) -> Optional[Config]:
    default_config_secret_name = os.environ.get('OAUTH2_PROXY_ADMISSION_SECRET_NAME', None)
    default_config_secret_namespace = os.environ.get('OAUTH2_PROXY_ADMISSION_SECRET_NAMESPACE', None)

    client = kd.K8sClient()
    
    raw_configuration = {}
    if default_config_secret_name:
        raw_configuration = client.secrets.get(default_config_secret_name, default_config_secret_namespace).data

    raw_overrides = {}
    if secret_name:
        raw_overrides = client.secrets.get(secret_name, secret_namespace).data
    
    for k, v in raw_overrides.items():
        raw_configuration[k] = v
    
    result = {}
    for k, v in raw_configuration.items():
        result[k] = base64.b64decode(v).decode('ascii')
    try:
        return Config.validate(result)
    except ValidationError:
        return None