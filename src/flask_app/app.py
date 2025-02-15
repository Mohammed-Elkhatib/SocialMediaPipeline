from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
import plotly.express as px

app = Flask(__name__)
# Path to the word frequencies JSON file
JSON_FILE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../data')


# Endpoint to get word frequencies as JSON
@app.route('/word_frequencies', methods=['GET'])
def get_word_frequencies():
    try:
        # Ensure the file exists before attempting to load it
        if not os.path.exists(JSON_FILE_DIR):
            return jsonify({"error": "Word frequency data not found"}), 404

        # Read the word frequencies from the JSON file
        with open(JSON_FILE_DIR, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Return the JSON data as a response
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route for displaying the bubble chart
@app.route('/visualization', methods=['GET'])
def show_bubble_chart():
    try:
        # Ensure the file exists before attempting to load it
        if not os.path.exists(JSON_FILE_DIR):
            return "Word frequency data not found", 404

        # Read the word frequencies
        with open(JSON_FILE_DIR, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Prepare data for the bubble chart
        words = [entry['word'] for entry in data]
        counts = [entry['count'] for entry in data]
        size = [entry['count'] * 10 for entry in data]  # Adjust the size of bubbles

        # Create a bubble chart using Plotly
        fig = px.scatter(x=words, y=counts, size=size, hover_name=words, title="Top 20 Word Frequencies Bubble Chart")

        # Generate HTML for the Plotly chart
        graph_html = fig.to_html(full_html=False)

        return render_template('index.html', graph_html=graph_html)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/word_frequencies.json')
def serve_json():
    # Serve the JSON file from the external directory
    return send_from_directory(JSON_FILE_DIR, 'word_frequencies.json')


if __name__ == '__main__':
    app.run(debug=True)
