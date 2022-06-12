"""
App level tests
"""
from app.main import app

def test_trailing_slashes():
    """
    Test for trailing slashes at the end of urls
    """
    exceptions = ('/',)
    assert all((route.path in exceptions or route.path[-1] != "/" for route in app.routes))
