import base64
import copy
import http
# import json
# import random
import logging
from typing import Callable
from fastapi.routing import APIRoute
import jsonpatch
from starlette.responses import StreamingResponse


logging.basicConfig(level=logging.DEBUG)

from models import WebhookRequest, WebhookResponse

from fastapi import FastAPI, Request, Response
app = FastAPI()

# class ValidationErrorLoggingRoute(APIRoute):
#     def get_route_handler(self) -> Callable:
#         original_route_handler = super().get_route_handler()

#         async def custom_route_handler(request: Request) -> Response:
#             req = await request.body()
#             logging.debug(' ' + req.decode())
#             response: Response = await original_route_handler(request)
#             logging.debug(' ' + response.body.decode())
#             return response

#         return custom_route_handler

# app.router.route_class = ValidationErrorLoggingRoute

@app.post("/mutate", response_model_exclude_none=True, response_model_by_alias=True)
async def mutate(request:WebhookRequest):
    response = WebhookResponse()
    response.api_version = request.api_version
    response.kind = request.kind

    response.response.uid = request.request.uid
    response.response.allowed = True

    pod_body = copy.deepcopy(request.request.object)
    if 'labels' not in pod_body.metadata.keys():
        pod_body.metadata['labels'] = {}
    pod_body.metadata['labels']['test'] = 'succesful'

    response.response.patch_type = 'JSONPatch'
    generated_jsonpatch = jsonpatch.make_patch(request.request.object.model_dump(), pod_body.model_dump())
    response.response.patch = base64.b64encode(generated_jsonpatch.to_string().encode()).decode()

    return response


@app.get("/healthz/live")
def liveness():
    return ''

@app.get("/healthz/ready")
def readiness():
    return ''

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)  # pragma: no cover