import json
from typing import Any, AnyStr, List

from llama_index.core.llms import ChatMessage
from llama_index.storage.chat_store.postgres import PostgresChatStore
from sqlalchemy import text


class CustomPostgresChatStore(PostgresChatStore):
    def _initialize(self, base: Any) -> None:
        """
        Override this fuction in "PostgresChatStore", because it creates table with
        name defined by itself
        """
        return

    def add_message(self, key: AnyStr, message: ChatMessage) -> None:
        """
        Add a message for a key

        :param key: unique key for a session, it's format should be "session_id:user_id"
        :param message: chat message
        """
        user_id, session_id = key.split(':')

        with self._session() as session:
            stmt = text(
                f"""
                INSERT INTO
                    {self.schema_name}.{self.table_name} (session_id, user_id, messages, updated_at)
                VALUES (:session_id, :user_id, CAST(:messages AS jsonb), NOW())
                ON CONFLICT (session_id, user_id)
                DO UPDATE SET
                    messages = chat_history.messages || CAST(:messages AS jsonb),
                    updated_at = NOW()
                """
            )

            params = {
                'session_id': session_id,
                'user_id': user_id,
                'messages': json.dumps([message.dict()])
            }

            session.execute(stmt, params)
            session.commit()

    async def async_add_message(self, key: AnyStr, message: ChatMessage) -> None:
        """
        Async version of Add a message for a key

        :param key: unique key for a session, it's format should be "session_id:user_id"
        :param message: chat message
        """
        user_id, session_id = key.split(':')

        async with self._async_session() as session:
            stmt = text(
                f"""
                INSERT INTO
                    {self.schema_name}.chat_history (session_id, user_id, messages, updated_at)
                VALUES (:session_id, :user_id, CAST(:messages AS jsonb), NOW())
                ON CONFLICT (session_id, user_id)
                DO UPDATE SET
                    messages = chat_history.messages || CAST(:messages AS jsonb),
                    updated_at = NOW()
                """
            )

            params = {
                'session_id': session_id,
                'user_id': user_id,
                'messages': json.dumps([message.dict()])
            }

            await session.execute(stmt, params)
            await session.commit()

    def get_messages(self, key: AnyStr) -> List[ChatMessage]:
        """
        Get messages for a key

        :param key: unique key for a session, it's format should be "session_id:user_id"
        :return: list of chat messages
        """
        user_id, session_id = key.split(':')

        with self._session() as session:
            stmt = text(
                f"""
                SELECT * FROM {self.schema_name}.{self.table_name}
                WHERE session_id = :session_id AND user_id = :user_id
                """
            )

            params = {
                'session_id': session_id,
                'user_id': user_id
            }

            result = session.execute(stmt, params).first()

            if result:
                result = result._asdict()

                return [
                    ChatMessage.model_validate(removed_message)
                    for removed_message in result['messages']
                ]

            return []

    async def aget_messages(self, key: AnyStr) -> List[ChatMessage]:
        """
        Async version of Get messages for a key

        :param key: unique key for a session, it's format should be "session_id:user_id"
        :return: list of chat messages
        """
        user_id, session_id = key.split(':')

        async with self._async_session() as session:
            stmt = text(
                f"""
                SELECT * FROM {self.schema_name}.{self.table_name}
                WHERE session_id = :session_id AND user_id = :user_id
                """
            )

            params = {
                'session_id': session_id,
                'user_id': user_id
            }

            result = await session.execute(stmt, params).first()._asdict()

            if result:
                return [
                    ChatMessage.model_validate(removed_message)
                    for removed_message in result['messages']
                ]
            return []
