from typing import Any, AnyStr, Dict, Optional

from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = 'Internal server error'

    def __init__(
        self,
        detail: Optional[AnyStr] = None,
        **kwargs: Dict[AnyStr, Any]
    ) -> None:  # pylint: disable=W0613
        detail = self.DETAIL if detail is None else detail

        super().__init__(
            status_code=self.STATUS_CODE,
            detail=detail,
            **kwargs
        )
