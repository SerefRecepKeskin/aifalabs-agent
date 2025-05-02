import logging
import logging.handlers
import os
import sys
from typing import AnyStr

from config import config


class CustomFormatter(logging.Formatter):
    """
    Logging formatter class for colored logs
    """

    # ANSI color codes
    pink = "\x1b[38;5;206m"
    green = "\x1b[38;5;47m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt) -> None:
        """
        Initializer of formatter class

        :param fmt: _description_
        """
        logging.Formatter.__init__(self)

        self.fmt = fmt
        self.formats = {
            logging.DEBUG: self.pink + self.fmt + self.reset,
            logging.INFO: self.green + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record) -> logging.Formatter.format:
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt.replace("\n", " ").strip())
        return formatter.format(record)


def init_logging(
    name: AnyStr,
    level: AnyStr = 'INFO',
    file: bool = True,
    stdout: bool = True,
) -> logging.Logger:
    """
    Initialize logging

    :param level: logging level
    :param file: enable file logging
    :param stdout: enable system out logging
    :return: initialized logger
    """
    fmt = "%(asctime)s %(levelname)-8s %(process)d [%(filename)s:%(lineno)s] %(message)s"
    root = logging.getLogger(name)
    file_formatter = CustomFormatter(fmt)
    formatter = logging.Formatter(fmt.replace("\n", " ").strip())

    # get logging level
    level = logging.getLevelName(level)
    if isinstance(level, str) and level.startswith("Level"):
        level = logging.INFO

    root.setLevel(level)
    root.propagate = False

    if stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(file_formatter)
        root.addHandler(stdout_handler)


    if file:
        file_path = os.environ.get(
            'LOGFILE',
            '/tmp/agent-service-backend.log'
        )
        file_handler = logging.handlers.WatchedFileHandler(file_path)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    return root
