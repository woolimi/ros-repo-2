"""LLM client stub — queries the LLM server for product zone lookup."""

import logging

logger = logging.getLogger(__name__)

LLM_HOST = 'localhost'
LLM_PORT = 8000


def query_product(name: str) -> dict:
    """Query LLM server for product zone. Returns {'zone_id': int | None}."""
    logger.info(f'[LLMClient] query_product({name!r})')
    return {'zone_id': None}
