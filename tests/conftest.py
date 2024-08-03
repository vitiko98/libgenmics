import logging

import pytest

logging.getLogger("vcr").setLevel("WARNING")


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": ["api_key"],
    }
