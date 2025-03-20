import time
import random
import logging
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from src.config import Config


def create_driver_options():
    """
    Create Chrome driver options with settings to avoid detection.

    Returns:
        Options: Configured Chrome options
    """
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{Config.DEBUGGER_PORT}")
    options.add_argument(f"user-data-dir={Config.USER_DATA_DIR}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={get_random_user_agent()}")
    return options


def start_chrome():
    """Launch Chrome with debugging enabled for Selenium to connect."""
    command = [
        Config.CHROME_PATH,
        f"--remote-debugging-port={Config.DEBUGGER_PORT}",
        f"--user-data-dir={Config.USER_DATA_DIR}",
        "--disable-dev-shm-usage",
        "--no-default-browser-check"
    ]
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info(f"Chrome started with debugging port {Config.DEBUGGER_PORT}")


def initialize_driver():
    """
    Initialize and return a configured Chrome WebDriver.

    Returns:
        WebDriver: Configured Chrome WebDriver
    """
    options = create_driver_options()
    driver = webdriver.Chrome(options=options)
    return driver


def wait_for_element(driver, by_method, selector, timeout=10):
    """
    Wait for an element to be present on the page.

    Args:
        driver: Selenium WebDriver
        by_method: By method (e.g., By.XPATH)
        selector: Element selector
        timeout: Maximum wait time in seconds

    Returns:
        WebElement: The found element

    Raises:
        TimeoutException: If element is not found within timeout
    """
    return WebDriverWait(driver, timeout).until(
        ec.presence_of_element_located((by_method, selector))
    )


def wait_for_tweets(driver, timeout=5):
    """
    Wait for tweets to load on the page.

    Args:
        driver: Selenium WebDriver
        timeout: Maximum wait time in seconds

    Returns:
        WebElement: The first tweet element found
    """
    return wait_for_element(driver, By.XPATH, "//article[@data-testid='tweet']", timeout)


def smooth_scroll(driver, scroll_pixels=300, max_scrolls=10,
                  random_delay=True, scroll_pause_time=0.5):
    """
    Smoothly scroll down a page with random delays to mimic human behavior.

    Args:
        driver: Selenium WebDriver instance
        scroll_pixels: Number of pixels to scroll each time
        max_scrolls: Maximum number of scroll operations
        random_delay: Whether to add random delays between scrolls
        scroll_pause_time: Base time to pause between scrolls in seconds

    Returns:
        int: Number of scrolls performed
    """
    logger = logging.getLogger(__name__)
    scroll_count = 0

    # Get initial scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(max_scrolls):
        # Calculate scroll amount (with slight randomization)
        actual_scroll = scroll_pixels + random.randint(-50, 50) if random_delay else scroll_pixels

        # Scroll down
        driver.execute_script(f"window.scrollBy(0, {actual_scroll});")
        scroll_count += 1

        # Add random delay to mimic human behavior
        if random_delay:
            time.sleep(scroll_pause_time + random.random())
        else:
            time.sleep(scroll_pause_time)

        # Check if we've reached the bottom of the page
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Try one more scroll before concluding we're at the bottom
            driver.execute_script(f"window.scrollBy(0, {scroll_pixels * 2});")
            time.sleep(scroll_pause_time * 2)

            newest_height = driver.execute_script("return document.body.scrollHeight")
            if newest_height == new_height:
                logger.info(f"Reached bottom of page after {scroll_count} scrolls")
                break

        last_height = new_height

    return scroll_count


def retry_on_stale_element(func, retries=3, delay=1.0):
    """
    Decorator to retry a function when StaleElementReferenceException occurs.

    Args:
        func: Function to retry
        retries: Number of retries
        delay: Delay between retries in seconds

    Returns:
        Function result or raises the last exception
    """

    def wrapper(*args, **kwargs):
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except StaleElementReferenceException as e:
                if attempt == retries - 1:
                    raise
                time.sleep(delay)

    return wrapper


def wait_for_element_visibility(driver, by_method, selector, timeout=10, check_interval=0.5):
    """
    Wait for an element to be visible on the page.

    Args:
        driver: Selenium WebDriver instance
        by_method: Selenium By method (e.g., By.ID, By.CSS_SELECTOR)
        selector: Element selector
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds

    Returns:
        bool: True if element became visible, False if timeout
    """
    logger = logging.getLogger(__name__)
    end_time = time.time() + timeout

    while time.time() < end_time:
        try:
            elements = driver.find_elements(by_method, selector)
            if elements and elements[0].is_displayed():
                return True
        except Exception as e:
            logger.debug(f"Exception while waiting for element: {e}")

        time.sleep(check_interval)

    logger.warning(f"Timeout waiting for element: {selector}")
    return False


def get_random_user_agent():
    """
    Return a random user agent string to help avoid detection.

    Returns:
        str: Random user agent string
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71"
    ]
    return random.choice(user_agents)
