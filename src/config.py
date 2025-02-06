# Central configuration
class Config:
    # Scraping
    MAX_TWEETS = 200
    STOP_DATE = "2024-12-31"
    SCROLL_SPEED = 100
    SCROLL_DELAY = 0.05
    MAX_RETRIES = 3

    # Kafka
    KAFKA_BROKER = "localhost:9092"
    KAFKA_TOPIC = "social-media-data"

    # Browser
    USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/90.0.4430.212 Safari/537.36")
    CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    USER_DATA_DIR = "C:\\selenium\\chrome-profile"
    DEBUGGER_PORT = 9222

    # Flask Configuration
    FLASK_HOST = '0.0.0.0'
    FLASK_PORT = 5000
