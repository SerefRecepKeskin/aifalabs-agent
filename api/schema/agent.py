from typing import AnyStr
from uuid import UUID

from pydantic import BaseModel


class MessageRequest(BaseModel):
    user_message: AnyStr
    session_identifier: UUID
    user_identifier: UUID


class MessageResult(BaseModel):
    bot_message: AnyStr
    message_identifier: UUID

