from .sse_connect import app 
from pydantic import BaseModel
import random
from random import randint
from datetime import datetime
import json
import re
from fastapi.responses import JSONResponse
from database.queries import SocialMediaQueries

print("Initializing endpoints...")

queries = SocialMediaQueries()
# Endpoint for pie chart data
@app.get("/api/pie-chart-data")
async def get_pie_chart_data():
    # Generate random data for the pie chart (percentage breakdown)
    data = [randint(10, 60) for _ in range(3)]  # Random data for 3 categories
    # Ensure the total is 100 by adjusting the last value
    total = sum(data)
    data[2] = 100 - (data[0] + data[1])

    labels = ["Positive", "Neutral", "Negative"]
    return {"labels": labels, "data": data} 

def calculate_virality(likes: int, retweets: int, comments: int) -> float:
    # Example formula to calculate virality based on likes, retweets, and comments
    return likes + (retweets * 2) + (comments * 1.5)


# Endpoint to get initial chart data
@app.get("/api/chart-data")
async def get_chart_data():
    return {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "data": [random.randint(5000, 40000) for _ in range(12)]
    }

# Endpoint to get updated chart data at intervals
@app.get("/api/chart-update")
async def update_chart_data():
    return {
        "data": [random.randint(5000, 40000) for _ in range(12)]
    }


# Endpoint for heatmap data
@app.get("/api/heatmap-data")
async def get_heatmap_data():
    # Generate random data for the heatmap
    z = [[randint(-10, 100) if randint(0, 1) else None for _ in range(5)] for _ in range(3)]  # 3x5 matrix with random numbers
    x = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    y = ['Morning', 'Afternoon', 'Evening']

    return {"x": x, "y": y, "z": z}


def load_word_data():
    word_data = queries.fetch_word_frequencies()
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


class ProgressData(BaseModel):
    label: str
    percentage: int
    color: str

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
    # Create data with random percentages and their corresponding colors
    data = [
        {"label": "January", "percentage": random.randint(0, 100), "color": ""},
        {"label": "February", "percentage": random.randint(0, 100), "color": ""},
        {"label": "March", "percentage": random.randint(0, 100), "color": ""},
        {"label": "April", "percentage": random.randint(0, 100), "color": ""},
        {"label": "May", "percentage": random.randint(0, 100), "color": ""}
    ]
    
    # Update color based on percentage
    for entry in data:
        entry["color"] = get_color_for_percentage(entry["percentage"])
    
    return {"data": data}


class EmployeeData(BaseModel):
    name: str
    position: str
    office: str
    age: int
    date_of_joining: str
    salary: str

def generate_random_data():
    positions = ["Software Engineer", "Javascript Developer", "Customer Support", "Product Manager", "Data Scientist"]
    offices = ["New York", "Singapore", "San Francisco", "London", "Tokyo"]
    salary_range = [80000, 100000, 120000, 140000, 160000, 180000, 200000]

    data = []
    for _ in range(5):  # Generate data for 5 employees
        name = f"Employee {random.randint(1, 100)}"
        position = random.choice(positions)
        office = random.choice(offices)
        age = random.randint(22, 50)
        date_of_joining = datetime.now().strftime("%Y/%m/%d")
        salary = f"${random.choice(salary_range):,}"
        
        data.append({
            "name": name,
            "position": position,
            "office": office,
            "age": age,
            "date_of_joining": date_of_joining,
            "salary": salary
        })
    
    return data

@app.get("/api/employee-data")
async def get_employee_data():
    data = generate_random_data()
    return {"data": data}

class SocialMediaData(BaseModel):
    total_likes: int
    total_followers: int
    total_comments: int
    total_shares: int

@app.get("/api/social-media-data", response_model=SocialMediaData)
async def get_social_media_data():
    return SocialMediaData(
        total_likes=random.randint(10000, 500000),
        total_followers=random.randint(100000, 1000000),
        total_comments=random.randint(1000, 100000),
        total_shares=random.randint(5000, 500000)
    )

def load_engagement_data_top_comments():
    data = queries.fetch_top_comments()
    return data

def load_engagement_data_top_likes():
    data = queries.fetch_top_comments()
    return data


topComments = load_engagement_data_top_comments()
topLikes = load_engagement_data_top_likes()
print(topComments)
print(topLikes)

@app.get("/api/bar-chart-data")
async def get_bar_chart_data():
    labels = [f"{post['date']} {post['time']}" for post in topComments]
    likes = [post["likes"] for post in topComments]
    retweets = [post["retweets"] for post in topComments]
    comments = [post["comments"] for post in topComments]
    contents = [post["content"] for post in topComments]  # Include content for tooltips

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
    labels = [f"{post['date']} {post['time']}" for post in topLikes]
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


from datetime import datetime
def to_unix_timestamp(date_str):
    return int(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timestamp())  # Convert to UNIX timestamp

@app.get("/api/bubble-chart-data")
async def get_bubble_chart_data():
    x_data = []
    y_data = []
    size_data = []
    text_data = []

    for item in topLikes:
        try:
            date_str = f"{item['date']} {item['time']}"

            # Virality calculation
            virality = calculate_virality(item['likes'], item['retweets'], item['comments'])

            if virality > 0:
                scaled_virality = virality * 0.1
                scaled_size = (item['likes'] + item['retweets'] + item['comments']) * 0.25

                x_data.append(to_unix_timestamp(date_str))  # Store adjusted timestamp
                y_data.append(scaled_virality)
                size_data.append(scaled_size)
                text_data.append(item['content'])

                print(f"Processed: {date_str} -> {to_unix_timestamp(date_str)}")  # Debugging output

        except Exception as e:
            print(f"Error processing item {item['id']}: {e}")

    return JSONResponse(content={
        'x': x_data,
        'y': y_data,
        'size': size_data,
        'text': text_data
    })


