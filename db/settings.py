from typing import AnyStr

from pydantic import Field
from pydantic_settings import BaseSettings

from config import config
from util.sting import String


class Settings(BaseSettings):
    @classmethod
    def get_uri(cls) -> AnyStr:
        """
        Get postgres async connection url

        :return: connection url
        """
        host = config.postgres.db_host
        port = config.postgres.db_port
        user = config.postgres.db_user
        password = config.postgres.db_password
        db = config.postgres.db_name

        uri = f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}'

        if String.is_empty(user) and String.is_empty(password):
            uri = f'postgresql+asyncpg://{host}:{port}/{db}'

        return uri

    # pylint: disable=unnecessary-lambda
    DATABASE_URL: AnyStr = Field(default_factory=lambda: Settings.get_uri())


settings = Settings()