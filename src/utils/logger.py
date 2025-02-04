import sys
import logging
from logging import Formatter, StreamHandler


class WindowsSafeStreamHandler(StreamHandler):
    def emit(self, record):
        stream = self.stream
        try:
            msg = self.format(record)
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            # Fallback to ASCII-only output
            msg = self.format(record).encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            stream.write(msg + self.terminator)
            self.flush()


class EmojiFormatter(Formatter):
    emoji_map = {
        'INFO': 'ℹ️ ',
        'WARNING': '⚠️ ',
        'ERROR': '❌ ',
        'CRITICAL': '🛑 ',
        'DEBUG': '🐛 '
    }

    def __init__(self):
        super().__init__('%(asctime)s %(message)s', datefmt='%H:%M:%S')

    def format(self, record):
        symbol = self.emoji_map.get(record.levelname, '>')
        message = super().format(record)
        return f"{symbol} {message}"


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Windows-safe handler
    console = WindowsSafeStreamHandler()
    console.setFormatter(EmojiFormatter())

    # File handler
    file = logging.FileHandler('scraping.log', encoding='utf-8')
    file.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(console)
    logger.addHandler(file)
