import pytest
from selenium import webdriver

BASE_URL = "https://opencart.abstracta.us/index.php?route=common/home"


@pytest.fixture
def driver():
    driver = webdriver.Chrome()   # open a new Chrome window
    driver.maximize_window()      # full size so all page elements are visible
    yield driver                  # hand the browser to the test
    driver.quit()                 # close the browser after the test finishes


def test_home_page_loads(driver):
    driver.get(BASE_URL)                  # go to the store home page
    assert driver.title == "Your Store"   # the page title should match