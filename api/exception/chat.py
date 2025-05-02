from api.exception.base import BaseHTTPException
from fastapi import status


class ChatResponseError(BaseHTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = 'Failed to create response'
