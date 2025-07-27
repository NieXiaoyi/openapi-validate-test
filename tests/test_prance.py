import pytest
import logging

from prance import ResolvingParser

with open('openapi/user.yml', 'r') as f:
    spec = f.read()


class TestPrance:
    def test_specification(self):
        parser = ResolvingParser('openapi/user.yml', backend='openapi-spec-validator')
        logging.info("API Specification: %s", parser.specification)
        