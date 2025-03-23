from fastapi import Query
from .sse_connect import app 
from pydantic import BaseModel
import re
from src.models.relational.tweets import TweetModel

print("Initializing endpoints...")

queries = TweetModel()

def calculate_engagement(likes: int, retweets: int, comments: int) -> float:
    # Example formula to calculate virality based on likes, retweets, and comments
    return likes + (retweets * 2) + (comments * 1.5)

# Endpoint to get chart data
@app.get("/api/chart-data")
async def get_virality_over_time(filter_by: str = Query("date", enum=["date", "post"])):
    """Fetch virality data filtered by either 'date' (aggregated) or 'post' (individual posts)."""
    engagement_data = queries.fetch_virality_data(filter_by=filter_by)

    if filter_by == "date":
        date_aggregated = {}
        for entry in engagement_data:
            post_date = entry["post_date"].strftime('%Y-%m-%d')  # Convert to string for JSON
            virality_score = entry["virality_score"]
            date_aggregated[post_date] = date_aggregated.get(post_date, 0) + virality_score

        x_data, y_data = zip(*sorted(date_aggregated.items())) if date_aggregated else ([], [])

    elif filter_by == "post":
        # Use both Date and Time for better distribution
        x_data = [entry["post_date"].strftime('%Y-%m-%d %H:%M:%S') for entry in engagement_data]
        y_data = [entry["virality_score"] for entry in engagement_data]

    return {"x": x_data, "y": y_data}



def process_heatmap_data(raw_data):
    # Build a dictionary mapping day -> {time_of_day: count, ...}
    data_dict = {}
    for row in raw_data:
        day = row["day"]
        tod = row["time_of_day"]
        count = row["count"]
        if day not in data_dict:
            data_dict[day] = {}
        data_dict[day][tod] = count

    # x-axis: sorted list of days (as strings)
    x = sorted(data_dict.keys())

    # y-axis: fixed time-of-day bins
    y = ["Morning", "Afternoon", "Evening"]

    # Build the z matrix: for each time bin (row), get the count for each day (column)
    z = []
    for tod in y:
        row_values = []
        for day in x:
            row_values.append(data_dict.get(day, {}).get(tod, 0))
        z.append(row_values)

    title = "Posts Activity Heatmap"
    return {"title": title, "x": x, "y": y, "z": z}

# Endpoint for heatmap data
@app.get("/api/heatmap-data")
async def get_heatmap_data():
    raw_data =  queries.fetch_heatmap_raw_data()
    processed_data = process_heatmap_data(raw_data)
    return processed_data



def load_word_data():
    word_data = queries.fetch_word_frequencies()
    return word_data

def load_hashtag_data():
    word_data = queries.fetch_hashtag_frequencies()
    return word_data

def detect_script(text):
    # Regular expressions for Arabic and English
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    english_pattern = re.compile(r'[A-Za-z]')

    if arabic_pattern.search(text):
        return "Arabic"
    elif english_pattern.search(text):
        return "English"
    
    return "Unknown"

# Endpoint to get language data with randomized frequencies
@app.get("/api/language-data")
async def get_word_data():
    word_data = load_word_data()  # Load data from JSON file
    for word_item in word_data:
        word_item["category"] = detect_script(word_item["word"])
    return {"data": word_data}

@app.get("/api/hashtag-data")
async def get_hashtag_data():
    word_data = load_hashtag_data()  # Load data from JSON file
    for word_item in word_data:
        word_item["category"] = detect_script(word_item["word"])
    return {"data": word_data}

def get_color_for_percentage(percentage: int) -> str:
    """Function to return a color based on the percentage value."""
    if percentage >= 80:
        return "bg-success"  # Green for 80% or more
    elif percentage >= 60:
        return "bg-info"  # Blue for 60%-79%
    elif percentage >= 40:
        return "bg-warning"  # Yellow for 40%-59%
    else:
        return "bg-danger"  # Red for below 40%

@app.get("/api/progress-data")
async def get_progress_data():
    # Calculate start_date (5 days ago) and end_date (today)
    end_date = datetime.now().date()  # Today's date
    start_date = end_date - timedelta(days=5)  # 5 days ago
    # Fetch the engagement data from the database
    results = queries.fetch_engagement_data(start_date=start_date,end_date=end_date)

    # Calculate the maximum engagement per post across the returned results for normalization
    if results:
        max_engagement = max(r["engagement_per_post"] for r in results)
    else:
        max_engagement = 0

    # Process the results: compute percentage and set label
    for r in results:
        # Calculate a percentage based on engagement per post relative to the maximum found
        r["percentage"] = (r["engagement_per_post"] / max_engagement * 100) if max_engagement > 0 else 0
        # Use the day as the label (or format it as you wish)
        r["label"] = r["day"]

    return {"data": results}

class SocialMediaData(BaseModel):
    total_likes: int
    total_posts: int
    total_comments: int
    total_shares: int

@app.get("/api/social-media-data", response_model=SocialMediaData)
async def get_social_media_data():
    results = queries.fetch_engagement_metrics()
    return SocialMediaData(
        total_likes=results["total_likes"],
        total_posts=results["total_posts"],
        total_comments=results["total_comments"],
        total_shares=results["total_retweets"]
    )

def load_engagement_data_top_comments():
    data = queries.fetch_top_comments()
    return data

def load_engagement_data_top_likes():
    data = queries.fetch_top_comments()
    return data

def load_engagement_data_top_retweets():
    data = queries.fetch_top_retweets()
    return data


topComments = load_engagement_data_top_comments()
topLikes = load_engagement_data_top_likes()
topRetweets = load_engagement_data_top_retweets()


@app.get("/api/bar-chart-data-comments")
async def get_bar_chart_data():
    labels = [f"{post['post_date']} {post['post_time']}" for post in topComments]
    likes = [post["likes"] for post in topComments]
    retweets = [post["retweets"] for post in topComments]
    comments = [post["comments"] for post in topComments]
    contents = [post["content"] for post in topComments]  # Include content for tooltipssq;

    return {
        "labels": labels,
        "datasets": [
            {"label": "Likes", "backgroundColor": "#4e73df", "data": likes, "content": contents},
            {"label": "Retweets", "backgroundColor": "#1cc88a", "data": retweets, "content": contents},
            {"label": "Comments", "backgroundColor": "#e74a3b", "data": comments, "content": contents},
        ]
    }

@app.get("/api/bar-chart-data-likes")
async def get_bar_chart_data_likes():
    labels = [f"{post['post_date']} {post['post_time']}" for post in topLikes]
    likes = [post["likes"] for post in topLikes]
    retweets = [post["retweets"] for post in topLikes]
    comments = [post["comments"] for post in topLikes]
    contents = [post["content"] for post in topLikes]

    return {
        "labels": labels,
        "datasets": [
            {"label": "Likes", "backgroundColor": "#4e73df", "data": likes, "content": contents},
            {"label": "Retweets", "backgroundColor": "#1cc88a", "data": retweets, "content": contents},
            {"label": "Comments", "backgroundColor": "#e74a3b", "data": comments, "content": contents},
        ]
    }

@app.get("/api/bar-chart-data-retweets")
async def get_bar_chart_data_likes():
    labels = [f"{post['post_date']} {post['post_time']}" for post in topRetweets]
    likes = [post["likes"] for post in topRetweets]
    retweets = [post["retweets"] for post in topRetweets]
    comments = [post["comments"] for post in topRetweets]
    contents = [post["content"] for post in topRetweets]

    return {
        "labels": labels,
        "datasets": [
            {"label": "Likes", "backgroundColor": "#4e73df", "data": likes, "content": contents},
            {"label": "Retweets", "backgroundColor": "#1cc88a", "data": retweets, "content": contents},
            {"label": "Comments", "backgroundColor": "#e74a3b", "data": comments, "content": contents},
        ]
    }



from datetime import datetime, time, timedelta
def to_unix_timestamp(date_str):
    return int(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timestamp())  # Convert to UNIX timestamp
