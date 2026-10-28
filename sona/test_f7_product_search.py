"""T007 - F7 Product Search (OpenCart demo store).
Tester: Sona Dheep Raja Balaji
Run: pytest sona/test_f7_product_search.py -v
"""
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

HOME_URL = "https://opencart.abstracta.us/index.php?route=common/home"
WAIT = 30  # the shared demo site (and an older Intel Mac) can be slow, so allow up to 30 seconds

# Locators used by every scenario
SEARCH_BOX = (By.CSS_SELECTOR, "#search input[name='search']")   # search box in the page header
SEARCH_BTN = (By.CSS_SELECTOR, "#search button")                  # magnifying-glass button next to it
RESULTS_PAGE = (By.ID, "input-search")                            # "Search Criteria" box, only on the results page
RESULT_NAMES = (By.CSS_SELECTOR, "#content .product-thumb h4 a")  # name link of each product found
EMPTY_TEXT = "There is no product that matches the search criteria."

# Evidence screenshots are saved in sona/screenshots/
SHOTS = Path(__file__).parent / "screenshots"
SHOTS.mkdir(exist_ok=True)


# Fixture: opens a fresh Chrome window for every test and closes it afterwards,
# so scenarios cannot affect each other (no shared cookies or session).
@pytest.fixture
def driver():
    d = webdriver.Chrome()   # Selenium Manager downloads the matching ChromeDriver automatically
    d.maximize_window()      # full size so the header search bar is visible
    yield d                  # hand the browser to the test
    d.quit()                 # always close the browser, even if the test fails


# Saves a screenshot into sona/screenshots/ as evidence for the report.
def shot(d, name):
    d.save_screenshot(str(SHOTS / f"{name}.png"))


# Opens the home page, types the keyword into the header search bar and clicks the search button.
def search(d, keyword):
    d.get(HOME_URL)                                                        # start from the home page, like a real user
    box = WebDriverWait(d, WAIT).until(EC.visibility_of_element_located(SEARCH_BOX))
    box.clear()                                                            # make sure the box is empty
    box.send_keys(keyword)                                                 # type the test keyword ("" types nothing)
    d.find_element(*SEARCH_BTN).click()                                    # click the search button
    WebDriverWait(d, WAIT).until(EC.url_contains("route=product/search"))  # the site moves to the results page
    WebDriverWait(d, WAIT).until(EC.visibility_of_element_located(RESULTS_PAGE))  # wait until it has loaded


# Returns the names of all products listed on the results page ([] if none).
def result_names(d):
    return [e.text for e in d.find_elements(*RESULT_NAMES)]


# Returns all visible text in the main content area, used to check messages.
def content_text(d):
    return " ".join(d.find_element(By.ID, "content").text.split())  # join text split over several lines


# Scenario 1 (valid input): search for an existing product name.
# Expected: the results page lists only matching products (MacBook, MacBook Air, MacBook Pro).
def test_t007_s1_existing_keyword(driver):
    search(driver, "MacBook")
    names = result_names(driver)
    print("Products found:", names)                                  # shown with pytest -s, useful for the report
    shot(driver, "T007-S1_existing_keyword")                         # evidence screenshot
    heading = driver.find_element(By.CSS_SELECTOR, "#content h1").text
    assert "MacBook" in heading, f"Page heading shows: {heading}"    # heading repeats the keyword
    assert len(names) >= 1, "No products were listed for 'MacBook'"  # at least one match is shown
    assert all("macbook" in n.lower() for n in names), f"Unrelated products listed: {names}"  # every match is relevant


# Scenario 2 (invalid input): search for a keyword that matches no product.
# Expected: no products are listed and the 'no product matches' message is shown.
def test_t007_s2_no_matching_product(driver):
    search(driver, "xyz123nothing")
    names = result_names(driver)
    shot(driver, "T007-S2_no_matching_product")
    assert names == [], f"Products were listed for a nonsense keyword: {names}"
    page = content_text(driver)
    assert EMPTY_TEXT in page, f"Defect: wrong or missing 'no match' message. Page shows: {page[-80:]}"  # user is told nothing matched


# Scenario 3 (empty input): click search without typing anything.
# Expected: the results page opens with no products listed and the 'no product matches' message.
def test_t007_s3_empty_keyword(driver):
    search(driver, "")
    names = result_names(driver)
    shot(driver, "T007-S3_empty_keyword")
    assert names == [], f"Products were listed for an empty search: {names}"
    page = content_text(driver)
    assert EMPTY_TEXT in page, f"Defect: wrong or missing 'no match' message. Page shows: {page[-80:]}"
