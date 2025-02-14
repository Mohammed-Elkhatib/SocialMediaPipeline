# api.py
from flask import Flask, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


@app.route('/api/tweets', methods=['GET'])
def get_tweets():
    """
    Endpoint to serve tweet data.
    """
    # Placeholder: In the future, fetch data from a datastore updated by Kafka.
    logger.info("Received request for tweet data.")
    return jsonify({"message": "This endpoint will serve tweet data."}), 200


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Endpoint to serve tweet statistics.
    """
    # Placeholder: In the future, fetch stats from a datastore updated by Kafka.
    logger.info("Received request for tweet statistics.")
    return jsonify({"message": "This endpoint will serve tweet statistics."}), 200


@app.route('/')
def home():
    """
    Home endpoint with API documentation.
    """
    logger.info("Received request for home page.")
    return jsonify({
        'message': 'Twitter Scraper API with Kafka Integration',
        'endpoints': ['/api/tweets', '/api/stats']
    })


if __name__ == '__main__':
    app.run(debug=True)
