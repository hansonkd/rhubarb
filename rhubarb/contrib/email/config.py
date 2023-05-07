import dataclasses
from typing import Optional

from rhubarb.env import int_env, float_env, bool_env, str_env
from aiosmtplib.smtp import DEFAULT_TIMEOUT


@dataclasses.dataclass(frozen=True)
class EmailConfig:
    hostname: Optional[str] = str_env("SMTP_HOSTNAME")
    port: Optional[int] = int_env("SMTP_PORT")
    sender: Optional[str] = str_env("SMTP_DEFAULT_SENDER")
    username: Optional[str] = str_env("SMTP_USERNAME")
    password: Optional[str] = str_env("SMTP_PASSWORD")
    timeout: Optional[float] = float_env("SMTP_TIMEOUT", DEFAULT_TIMEOUT)
    use_tls: bool = bool_env("SMTP_USE_TLS", False)
    start_tls: Optional[bool] = bool_env("SMTP_START_TLS")
    validate_certs: bool = bool_env("SMTP_VALIDATE_CERTS")
    client_cert: Optional[str] = str_env("SMTP_CLIENT_CERT")
    client_key: Optional[str] = str_env("SMTP_CLIENT_KEY")
