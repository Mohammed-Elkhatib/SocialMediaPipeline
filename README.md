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
│   │   └── consumers/
│   │       ├── base.py       # Abstract consumer class
│   │       ├── storage.py    # Database writer
│   │       └── stats.py      # Real-time statistics
│   │
│   │
│   ├── models/               # Database interaction
│   │   ├── relational/       # SQL tables
│   │   │   ├── tweets.py     # Tweet SQL model
│   │   │   └── connection.py # Database connection
│   │   │ 
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
├── database_mariadb.sql       Persistant storage schema
├── docker-compose.yml        # Docker configuration
├── README.md                 # Project documentation
├── .gitignore                # Git ignore file
└── .env                      # Environment variables 
```
## Prerequisites

- **XAMPP** – Required for MySQL database.
- **Docker Desktop** – Required for running Kafka container.
- **Python 3.8+** – Ensure you have Python installed.
- **Python Editor** – [PyCharm](https://www.jetbrains.com/pycharm/) is recommended.
- **Google Chrome** – Required for web scraping.

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

3. **Database Setup:**

   - **Start XAMPP:** Start the Apache and MySQL services.
   - **Create Database:** Open `http://localhost/phpmyadmin/` in your browser and create a new database named `social_media_pipeline`.
   - **Import Schema:** Import the `database_mariadb.sql` file to create the necessary tables.
   
   *Note: You can use any other database management tool to create the database and tables.*

4. **Start Docker Containers:**

   Run this command to start Docker containers. This step is required every time you run the project. On the first run, Docker will pull and configure the necessary images.
   
   ```bash
   docker compose up -d
   ```

5. **Create Kafka Topic:**

   Create the Kafka topic and start the consumer by running:
   
   ```bash
   docker exec -it kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic social-media-data --from-beginning
   ```

6. **Prepare Chrome for Scraping:**

   Open Windows PowerShell and run:
   
   ```powershell
   Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -Argumentlist "--remote_debugging-port=9222", "--user-data-dir=C:\selenium\chrome-profile"
   ```
   
   Then, sign in to x.com in the opened instance before closing the browser.

## Running the Application

### Scrape Twitter and Process Data

You can run different components of the pipeline:

1. **Scrape Twitter data:**

   ```bash
   python src/main.py --mode scrape --username ALJADEEDNEWS
   ```

2. **Process data with consumers:**

   ```bash
   python src/main.py --mode consume
   ```

3. **Run the full pipeline:**

   ```bash
   python src/main.py --mode all --username ALJADEEDNEWS
   ```

### View Kafka Messages

To view messages in the Kafka topic:

```bash
docker exec -it kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic social-media-data \
  --from-beginning
```

### Query Database

You can connect to the MySQL database through phpMyAdmin:
- Open http://localhost/phpmyadmin in your browser
- Login with your XAMPP MySQL credentials (default username: root, no password)
- Select the `social_media_pipeline` database to view the tables

## Extending the Project

### Adding New Social Media Platforms

To add support for a new platform:
1. Create a new extractor class specific to that platform
2. Update the scrape controller to handle the new platform
3. Add platform-specific parsing logic

### Enhanced Analytics

The existing database schema supports:
- Word frequency analysis
- Engagement metrics tracking
- Temporal analysis of posts

## Troubleshooting

### Common Issues

1. **Chrome Debugging Connection Fails**:
   - Ensure Chrome is running with the debugging port open
   - Check that the port number matches your configuration
   - Make sure you're signed into the social media platform

2. **Kafka Connection Issues**:
   - Verify Docker container is running: `docker ps`
   - Check Kafka logs: `docker logs kafka`

3. **Database Connection Errors**:
   - Verify XAMPP MySQL service is running in XAMPP Control Panel
   - Check your database credentials in the `.env` file
   - Ensure the database and tables are created

### Getting Help

If you encounter problems, please:
1. Check the logs in the `logs/` directory
2. Open an issue on the GitHub repository with details about the error
