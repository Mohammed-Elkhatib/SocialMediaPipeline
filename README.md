Project Structure:
social-media-pipeline/
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

Prerequisites:
 -Docker Desktop
 -Python
 -Python Editor (Preferably Pycharm)

Steps to run the project:
 -git clone https://github.com/Mohammed-Elkhatib/SocialMediaPipeline.git
 -pip install -r requirements.txt (pycharm will do this step automatically and create the virtual environment .env)
 -docker compose up -d (this step has to be done everytime everything else just once, however the first time it will pull the image install and configure it from that point it will only run the image)
 -docker exec -it kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic social-media-data --from-beginning (this will create the topic)
 -open Windows powershell and type this command: Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -Argumentlist "--remote_debugging-port=9222", "--user-data-dir=C:\selenium\chrome-profile" (this is necessary for scrapping)
 -In the opened instance sign in to x.com then close it 
 -run main.py (executes scrapper and producer)
 -run src/kafka/consumers/consumer.py to consume data from kafka
