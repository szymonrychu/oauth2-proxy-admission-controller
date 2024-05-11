import base64
import json
from typing import Any


def b64dec(data: str) -> str:
    return base64.b64decode(data.encode("utf-8")).decode("utf-8")


def b64enc(data: str) -> str:
    return base64.b64encode(data.encode("utf-8")).decode("utf-8")


def b64dec_json(data: str) -> Any:
    return json.loads(b64dec(data))


def b64enc_json(data: Any) -> str:
    return b64enc(json.dumps(data))
