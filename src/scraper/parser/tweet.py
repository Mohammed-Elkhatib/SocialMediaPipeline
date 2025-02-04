import time


def get_tweet_id(tweet, username):
    try:
        time_element = tweet.find('time')
        if time_element and time_element.has_attr('datetime'):
            clean_datetime = time_element['datetime'].split('.')[0].replace('Z', '').replace('T', ' ')
            return f"{username}_{clean_datetime}"
        return f"{username}_{time.time()}"
    except Exception as e:
        return f"{username}_{time.time()}"


def get_tweet_time(tweet):
    try:
        time_element = tweet.find('time')
        if time_element and time_element.has_attr('datetime'):
            clean_datetime = time_element['datetime'].split('.')[0].replace('Z', '')
            return tuple(clean_datetime.split('T'))
        return "N/A", "N/A"
    except:
        return "N/A", "N/A"
