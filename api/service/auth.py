from typing import AnyStr
from fastapi import HTTPException, status
from config import config

class AuthService:
    @staticmethod
    def validate_api_key(api_key: AnyStr) -> bool:
        """
        Validate API key
        
        :param api_key: API key from request header
        :return: True if valid, False otherwise
        """
        return api_key == config.app.api_key

    @staticmethod
    def check_auth(api_key: AnyStr) -> None:
        """
        Check authentication and raise exception if invalid
        
        :param api_key: API key from request header
        :raises: HTTPException if api key is invalid
        """
        if not AuthService.validate_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
