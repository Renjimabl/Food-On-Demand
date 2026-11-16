import os
import pytest
from dotenv import load_dotenv

load_dotenv()  # reads the .env file


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", "https://py.softlandindia.net/dine_flash_buffet/login/")


@pytest.fixture(scope="session")
def valid_username():
    return os.getenv("LOGIN_USERNAME")


@pytest.fixture(scope="session")
def valid_password():
    return os.getenv("LOGIN_PASSWORD")


@pytest.fixture
def login_page(page, base_url):
    from pages.login_page import LoginPage
    lp = LoginPage(page, base_url)
    lp.open()
    return lp


@pytest.fixture
def admin(page, base_url, valid_username, valid_password):
    """Browser logged in as the company admin (shared by the module test files)."""
    from pages.login_page import LoginPage
    lp = LoginPage(page, base_url)
    lp.open()
    lp.login(valid_username, valid_password)
    assert not lp.is_on_login_page(), f"Admin login failed. popups={lp.dialogs}"
    return lp
