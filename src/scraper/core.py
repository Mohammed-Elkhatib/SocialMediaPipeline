import time
import logging
from selenium import webdriver
from bs4 import BeautifulSoup
from src.config import Config
from .browser.driver import create_driver_options, start_chrome
from .browser.navigation import smooth_scroll, wait_for_tweets
from .parser.tweet import get_tweet_id, get_tweet_time
from .parser.interactions import extract_interactions, parse_counts


def scrape_twitter(username: str, kafka_sender) -> None:
    """Main scraping workflow with progressive backoff and smart waiting"""
    # Initialize browser
    start_chrome()
    time.sleep(4)

    options = create_driver_options()
    driver = webdriver.Chrome(options=options)

    seen_ids = set()
    retries = Config.MAX_RETRIES  # Initialize retries counter outside loop

    try:
        logging.info(f"🚀 Starting scrape for @{username}")
        driver.get(f"https://x.com/{username}")
        wait_for_tweets(driver)

        while len(seen_ids) < Config.MAX_TWEETS and retries > 0:
            smooth_scroll(driver)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            current_tweets = soup.find_all('article', {'data-testid': 'tweet'})

            new_tweets = 0
            for tweet in current_tweets:
                try:
                    if len(seen_ids) >= Config.MAX_TWEETS:
                        break

                    if tweet.find('span', string='Promoted'):
                        continue

                    tweet_id = get_tweet_id(tweet, username)
                    if tweet_id in seen_ids:
                        continue

                    text_element = tweet.find('div', {'data-testid': 'tweetText'})
                    content = text_element.get_text(strip=True) if text_element else "N/A"

                    buttons = tweet.find_all('button', {'role': 'button'})
                    interactions = extract_interactions(buttons)
                    counts = parse_counts(interactions)
                    date, tweet_time = get_tweet_time(tweet)

                    if date < Config.STOP_DATE:
                        logging.warning(f"🛑 Reached historical limit at {date}")
                        return

                    tweet_data = {
                        'id': tweet_id,
                        'date': date,
                        'time': tweet_time,
                        'content': content,
                        **counts
                    }
                    kafka_sender.send(tweet_data)
                    seen_ids.add(tweet_id)
                    new_tweets += 1

                except Exception as e:
                    logging.error(f"❌ Error processing tweet: {str(e)}")

            if new_tweets > 0:
                retries = Config.MAX_RETRIES + 1 # Reset counter on success
                logging.info(f"📦 Collected {new_tweets} new tweets (Total: {len(seen_ids)})")
            else:
                logging.warning("⚠️  No new tweets in loaded content")
                retries -= 1
                if retries > 0:
                    attempt_number = Config.MAX_RETRIES - retries + 1
                    sleep_time = min(2 ** attempt_number, 10)
                    logging.warning(f"⏳ Retry #{attempt_number} for {sleep_time}s")
                    time.sleep(sleep_time)
                else:
                    logging.error("🔴 Max retries reached. Stopping.")

    except Exception as e:
        logging.error(f"💥 Critical error: {str(e)}")
        raise

    finally:
        driver.quit()
        logging.info(f"✅ Final count: {len(seen_ids)}/{Config.MAX_TWEETS} tweets")
        if len(seen_ids) >= Config.MAX_TWEETS:
            logging.info("🎯 Target reached successfully")
        else:
            logging.warning("⚠️  Ended before reaching target")