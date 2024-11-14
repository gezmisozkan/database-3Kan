from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': '3kan'
}

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    teams = []
    matches = []
    selected_team = None

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch all team names
    cursor.execute("SELECT DISTINCT home_team_name FROM matches")
    teams = [team[0] for team in cursor.fetchall()]

    if request.method == 'POST':
        selected_team = request.form['team']

        # Fetch matches for the selected team
        query = """
        SELECT match_id, home_team_name, away_team_name, home_team_score, away_team_score
        FROM matches
        WHERE home_team_name = %s OR away_team_name = %s
        ORDER BY match_id DESC
        """
        cursor.execute(query, (selected_team, selected_team))
        matches = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('index.html', teams=teams, matches=matches, selected_team=selected_team)

if __name__ == '__main__':
    app.run(debug=True)
