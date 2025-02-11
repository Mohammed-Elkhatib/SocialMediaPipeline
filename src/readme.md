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
 docker compose up -d
