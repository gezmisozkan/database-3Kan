# Front end görünümleriyle al
#Görünümlerin tek bir dosyada toplanmasına gerek kalmadığını göstermek için kullanılır. 
from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from sqlalchemy.sql import text

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    return render_template("base.html", user=current_user)

@views.route('/teams', methods=['GET', 'POST'])
@login_required
def teams():
    teams = []
    matches = []
    selected_team = None

    # Use current_app to access the MySQL engine
    mysql_engine = current_app.mysql_engine

    # Open a connection to the MySQL database
    with mysql_engine.connect() as connection:
        # Fetch all team names
        query = "SELECT DISTINCT home_team_name FROM matches"
        result = connection.execute(text(query))
        teams = [row[0] for row in result]

        if request.method == 'POST':
            selected_team = request.form['team']

            # Fetch matches for the selected team
            match_query = """
            SELECT match_id, home_team_name, away_team_name, home_team_score, away_team_score
            FROM matches
            WHERE home_team_name = :team OR away_team_name = :team
            ORDER BY match_id DESC
            """
            result = connection.execute(text(match_query), {"team": selected_team})
            matches = result.fetchall()

    return render_template("teams.html", teams=teams, matches=matches, selected_team=selected_team)
