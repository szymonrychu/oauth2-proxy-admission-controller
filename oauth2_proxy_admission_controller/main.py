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
    if settings.SSL_KEY_PATH and settings.SSL_CERT_PATH:
        kwargs["ssl_keyfile"] = settings.SSL_KEY_PATH
        kwargs["ssl_certfile"] = settings.SSL_CERT_PATH
    uvicorn.run("oauth2_proxy_admission_controller.app:app", host=str(settings.HOST), port=settings.PORT, **kwargs)


if __name__ == "__main__":
    serve()
