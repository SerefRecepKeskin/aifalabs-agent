from typing import AnyStr


class String:  # pylint: disable=too-few-public-methods
    """
    String class
    """
    @staticmethod
    def is_empty(text: AnyStr) -> bool:
        """
        Return true if string is empty, false otherwise

        :param text: text
        :return: true if empty, false otherwise
        """
        if text is None or not isinstance(text, str):
            return True

        return len(text) == 0
