import os
from .log import init_logging



logger = init_logging(
    'agent-service-api',
    file=False,
    stdout=True)
