import subprocess
import time
from selenium.webdriver.chrome.options import Options
from src.config import Config


def create_driver_options():
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{Config.DEBUGGER_PORT}")
    options.add_argument(f"user-data-dir={Config.USER_DATA_DIR}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={Config.USER_AGENT}")
    return options


def start_chrome():
    command = [
        Config.CHROME_PATH,
        f"--remote-debugging-port={Config.DEBUGGER_PORT}",
        f"--user-data-dir={Config.USER_DATA_DIR}",
        "--disable-dev-shm-usage",
        "--no-default-browser-check"
    ]
    chrome_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)  # Wait for Chrome to start up
    return chrome_process  # Return the process instance


def stop_chrome(chrome_process):
    """Stop the Chrome process after scraping is done."""
    chrome_process.terminate()  # Terminates the process
    chrome_process.wait()  # Wait for the process to terminate
