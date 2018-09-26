import os
import py
import pytest

_TEST_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def datadir():
    return py.path.local(os.path.join(_TEST_DIR, 'data'))
