import subprocess
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
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
