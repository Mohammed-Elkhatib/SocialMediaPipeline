import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from src.config import Config


def smooth_scroll(driver):
    """Preserved smooth scrolling functionality"""
    for _ in range(10):
        driver.execute_script(f"window.scrollBy(0, {Config.SCROLL_SPEED})")
        time.sleep(Config.SCROLL_DELAY)


def wait_for_tweets(driver, timeout=5):
    return WebDriverWait(driver, timeout).until(
        ec.presence_of_element_located((By.XPATH, "//article[@data-testid='tweet']"))
    )
