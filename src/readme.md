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

 gt clone https://github.com/Mohammed-Elkhatib/SocialMediaPipeline.git
 pip install -r requirements.txt
 docker compose up -d (this step has to be done everytime everything else just once)
 docker exec -it kafka /opt/bitnami/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic social-media-data --from-beginning
 Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" -Argumentlist "--remotr_debugging-port=9222", "--user-data-dir=C:\selenium\chrome-profile"
 In the openned instance sign in to x.com then close it 
 run main.py (excutes scrapper and producer)
 run src/kafka/consumers/consumer.py to consume data from kafka