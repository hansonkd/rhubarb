import dataclasses
from email.message import EmailMessage
from typing import Sequence

import aiosmtplib
from aiosmtplib import SMTPResponse

from rhubarb.config import config


async def send(
    message: EmailMessage, sender: str | None, recipients: str | Sequence[str] | None
) -> tuple[dict[str, SMTPResponse], str]:
    conf = config()
    kwargs = dataclasses.asdict(conf.email)
    if recipients is not None:
        kwargs["recipients"] = recipients

    if sender is not None:
        kwargs["sender"] = sender
    return await aiosmtplib.send(message, **kwargs)
