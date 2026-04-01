"""Auth route tests."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_login_page_renders(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'로그인' in resp.data
