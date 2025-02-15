# Social Media Pipeline

A project to scrape social media data, process it with Kafka, and store it in a database.

## Project Structure
```social-media-pipeline/
├── src/
│   ├── scraper/
│   │   ├── browser/          # Browser-related operations
│   │   │   ├── driver.py     # Chrome setup/management
│   │   │   └── navigation.py # Scrolling, pagination
│   │   ├── parser/           # Content extraction
│   │   │   ├── tweet.py      # Individual tweet parsing
│   │   │   └── interactions.py # Likes/retweets extraction
│   │   └── core.py           # Main scraping orchestration
│   │
│   ├── kafka/
│   │   ├── producer.py       # KafkaSender class
│   │   ├── consumers/
│   │   │   ├── base.py       # Abstract consumer class
│   │   │   ├── storage.py    # Database writer
│   │   │   └── stats.py      # Real-time statistics
│   │   └── schemas.py        # Data validation schemas
│   │
│   ├── models/               # Database interaction
│   │   ├── relational/       # SQL tables
│   │   │   └── tweets.py     # Tweet SQL model
│   │   └── graph/            # Future ontology storage
│   │       └── nodes.py      # Graph node definitions
│   │
│   ├── utils/
│   │   ├── logging.py        # Log configuration
│   │   ├── browser.py        # Smooth scroll, retry logic
│   │   └── data_helpers.py   # ID generation, date parsing
│   │
│   ├── config.py             # Central configuration
│   └── main.py               # Entry point
│
├── tests/                    # Future test cases
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables 
```
## Prerequisites

- **Docker Desktop** – Required for running Docker containers.
- **Python** – Ensure you have Python installed.
- **Python Editor** – [PyCharm](https://www.jetbrains.com/pycharm/) is recommended.

## Setup and Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Mohammed-Elkhatib/SocialMediaPipeline.git
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
   
   *Note: If you’re using PyCharm, it may automatically install dependencies and create the virtual environment using the provided `.env` file.*

3. **Start Docker Containers:**

   Run this command to start Docker containers. This step is required every time you run the project. On the first run, Docker will pull and configure the necessary images.
   
   ```bash
   docker compose up -d
   ```

4. **Create Kafka Topic:**

   Create the Kafka topic and start the consumer by running:
   
   ```bash
   docker exec -it kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic social-media-data --from-beginning
   ```

5. **Prepare Chrome for Scraping:**

   Open Windows PowerShell and run:
   
   ```powershell
   Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -Argumentlist "--remote_debugging-port=9222", "--user-data-dir=C:\selenium\chrome-profile"
   ```
   
   Then, sign in to x.com in the opened instance before closing the browser.

6. **Run the Project:**

   - **Scraping and Producing Data:**
     
     ```bash
     python main.py
     ```
     
   - **Consuming Data:**
     
     In another terminal, run:
     
     ```bash
     python src/kafka/consumers/consumer.py
     ```

## Additional Information

- **Configuration:** Adjust settings in `config.py` as needed.
- **Testing:** Future tests will be located in the `tests/` directory.
- **Logging:** Logs are set up via `src/utils/logging.py`.
