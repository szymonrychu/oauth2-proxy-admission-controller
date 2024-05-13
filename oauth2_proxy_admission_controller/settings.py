import logging
from enum import Enum
from typing import Optional, Union

from pydantic import AnyUrl, BaseSettings, IPvAnyAddress, validator
from yarl import URL

logger = logging.getLogger(__name__)


def get_connection_string(
    uri: str, *, username: Optional[str] = None, password: Optional[str] = None, port: Optional[int] = None
):
    url = URL(uri).with_user(username).with_password(password)
    if port is not None:
        url = url.with_port(port)

    return url.human_repr()


class AmqpDsn(AnyUrl):
    allowed_schemes = {"amqp"}
    user_required = True


class Settings(BaseSettings):
    class LogLevel(Enum):
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARN = "WARN"
        WARNING = "WARNING"
        ERROR = "ERROR"
        CRITICAL = "CRITICAL"

    DEBUG: bool = False
    HOST: Union[AnyUrl, IPvAnyAddress] = "0.0.0.0"
    PORT: int = 8080
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    SSL_KEY_PATH: str = None
    SSL_CERT_PATH: str = None

    @validator("PORT")
    def validate_PORT(v):
        return int(v) if isinstance(v, str) else v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

logging.basicConfig(level=settings.LOG_LEVEL.value, format=settings.LOG_FORMAT)
