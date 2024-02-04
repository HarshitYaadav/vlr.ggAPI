from flask import Flask, jsonify, request
from CombinedStats import CombinedStats
from scraper import Matches
from matchResults import get_match_results
from match_stats import MatchStats
import firebase_admin
from firebase_admin import credentials, db
import uuid
from jsonRoster import PlayerScraper  # Import the new PlayerScraper class


app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("C:\\Users\\harsh\\PycharmProjects\\scrapperFlask\\Api key\\key.json")

@app.route('/match_schedule', methods=['GET'])
def get_match_schedule():
    schedule = Matches.api_ready_match_schedule()

    # Refresh data for match_schedule
    store_in_firebase('/match_schedule', schedule, refresh=True)
    return jsonify(schedule)

@app.route('/match_results', methods=['GET'])
def get_match_results_route():
    url = "https://vlr.gg/matches/results"
    results = get_match_results(url, limit=15)
    # Store results in Firebase
    store_in_firebase('/match_results', results)
    return jsonify(results)

# New endpoint to get combined stats using match link as a parameter
#http://127.0.0.1:5000/match_roster?match_url=/
@app.route('/match_roster', methods=['GET'])
def get_combined_stats():
    try:
        match_url = request.args.get('match_url')
        if not match_url:
            return jsonify({"error": "Missing match_url parameter"}), 400

        combined_stats = CombinedStats(match_url)
        stats_data = combined_stats.extract_combined_stats()

        # Store stats_data in Firebase uniquely
        store_in_firebase('/match_roster', stats_data)

        return jsonify(stats_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/match_stats', methods=['GET'])
def get_match_stats_route():
    try:
        match_url = request.args.get('match_url')
        if not match_url:
            return jsonify({"error": "Missing match_url parameter"}), 400

        # Use the MatchStats class to get match stats
        match_stats_instance = MatchStats()
        match_stats_list = match_stats_instance.get_match_stats(f'https://www.vlr.gg{match_url}')

        if not match_stats_list:
            return jsonify({"error": "Failed to retrieve match stats"}), 500

        for match_stats in match_stats_list:
            # Store each match separately in Firebase
            store_in_firebase('/match_stats', match_stats)

        return jsonify(match_stats_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def store_in_firebase(path, data, refresh=False):
    ref = db.reference(path)

    if refresh:
        for match_stats in data:
            ref.push().set(match_stats)
    else:
        # Generate a unique key based on team names with a unique identifier
        team1_name = data.get("team1_name", "UnknownTeam1")
        team2_name = data.get("team2_name", "UnknownTeam2")

        # Generate a unique identifier (UUID)
        unique_id = str(uuid.uuid4().hex)

        # Combine team names and unique identifier in the key
        unique_key = f"{team1_name}_{unique_id}_{team2_name}"

        # Set data with the custom key
        ref.child(unique_key).set(data)

# New endpoint to get player rosters using event URL as a parameter
# http://127.0.0.1:5000/event_roster?url=https://www.vlr.gg/event/1924/champions-tour-2024-pacific-kickoff
@app.route('/event_roster', methods=['GET'])
def get_event_roster():
    try:
        event_url = request.args.get('url')
        if not event_url:
            return jsonify({"error": "Missing url parameter"}), 400

        player_scraper = PlayerScraper(event_url)
        event_data = player_scraper.scrape_event_data()
        event_data["event_name"] = event_url.split('/')[-1]  # Extract event name directly from the URL

        # Store event_data in Firebase uniquely
        store_event_roster_in_firebase('/event_roster', event_data)

        return jsonify(event_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



def store_event_roster_in_firebase(path, data):
    ref = db.reference(path)

    # Extract event name from the provided URL
    event_name = data.get("event_name", "UnknownEvent")

    # Replace spaces and special characters with dashes for a clean node name
    event_node_name = event_name.lower().replace(" ", "-").replace("/", "-")

    # Set data with the custom key
    ref.child(event_node_name).set(data)




if __name__ == '__main__':
    app.run(debug=True)
