def extract_interactions(buttons):
    interactions = {}
    for btn in buttons:
        testid = btn.get('data-testid', '')
        label = btn.get('aria-label', '')
        if testid in ['like', 'retweet', 'reply']:
            interactions[testid] = label
    return interactions


def parse_counts(interactions):
    return {
        'likes': int(interactions.get('like', '0').split()[0].replace(',', '')) if 'like' in interactions else 0,
        'retweets': int(interactions.get('retweet', '0').split()[0].replace(',', '')) if 'retweet' in interactions else 0,
        'comments': int(interactions.get('reply', '0').split()[0].replace(',', '')) if 'reply' in interactions else 0
    }