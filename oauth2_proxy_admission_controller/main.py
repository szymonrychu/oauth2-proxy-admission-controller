import logging

import uvicorn

from oauth2_proxy_admission_controller.settings import settings

logger = logging.getLogger(__name__)


def serve():
    kwargs = {}
    if settings.DEBUG:
        kwargs["reload"] = True
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = settings.LOG_FORMAT
    uvicorn.run("oauth2_proxy_admission_controller.app:app", host=str(settings.HOST), port=settings.PORT, **kwargs)


if __name__ == "__main__":
    serve()
