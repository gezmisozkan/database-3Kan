# Front end görünümleriyle al
#Görünümlerin tek bir dosyada toplanmasına gerek kalmadığını göstermek için kullanılır. 
from flask import Blueprint, render_template, request, current_app, g
from flask_login import login_required, current_user
from sqlalchemy.sql import text

views = Blueprint('views', __name__)

@views.before_app_request
def load_recent_seasons():
    """
    This function loads the 5 most recent unique years to be displayed in the navbar.
    """
    if not hasattr(g, 'recent_seasons'):
        mysql_engine = current_app.mysql_engine
        with mysql_engine.connect() as connection:
            # Load the 5 most recent years where seasons exist
            recent_years_query = "SELECT DISTINCT season FROM seasons ORDER BY season DESC LIMIT 5"
            recent_years_result = connection.execute(text(recent_years_query))
            g.recent_seasons = [row[0] for row in recent_years_result.fetchall()]  # Use row[0] for season


@views.route('/seasons/<int:year>', methods=['GET'])
@login_required
def season_tiers(year):
    """
    This view displays all available tiers for the selected season year.
    """
    tiers = []
    mysql_engine = current_app.mysql_engine
    with mysql_engine.connect() as connection:
        # Load all season_id and tiers for this specific year
        tier_query = """
            SELECT season_id, tier 
            FROM seasons 
            WHERE season = :season 
            ORDER BY tier
        """
        result = connection.execute(text(tier_query), {'season': year})
        tiers = [{'season_id': row[0], 'tier': row[1]} for row in result.fetchall()]  # Use row[0] and row[1] to access season_id and tier

    return render_template("season_tiers.html", year=year, tiers=tiers)

@views.route('/')
def home():
    return render_template("base.html", user=current_user)

@views.route('/teams', methods=['GET'])
@login_required
def teams():
    """
    This view displays a list of teams and allows users to search for a team by name.
    """
    teams = []
    search_query = request.args.get('search', '')

    mysql_engine = current_app.mysql_engine
    with mysql_engine.connect() as connection:
        if search_query:
            team_query = "SELECT team_id, team_name FROM teams WHERE team_name LIKE :search ORDER BY team_name"
            result = connection.execute(text(team_query), {'search': f'%{search_query}%'})
        else:
            team_query = "SELECT team_id, team_name FROM teams ORDER BY team_name"
            result = connection.execute(text(team_query))
        
        teams = result.fetchall()
    
    return render_template("teams.html", teams=teams, search_query=search_query)

@views.route('/teams-2', methods=['GET', 'POST'])
def teams2():
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

    return render_template("teams2.html", teams=teams, matches=matches, selected_team=selected_team)

@views.route('/seasons', methods=['GET'])
def search_seasons():
    mysql_engine = current_app.mysql_engine

    # Get search parameters from the request
    season = request.args.get('season')
    tier = request.args.get('tier')
    division = request.args.get('division')

    # Build the query dynamically
    query = "SELECT key_id, season_id, season, tier, division, subdivision, winner, count_teams FROM Seasons WHERE 1=1"
    params = {}

    if season:
        query += " AND season = :season"
        params['season'] = season
    if tier:
        query += " AND tier = :tier"
        params['tier'] = tier
    if division:
        query += " AND division = :division"
        params['division'] = division

    # Execute the query
    with mysql_engine.connect() as connection:
        seasons = connection.execute(text(query), params)

    # Render the template with filtered data
    return render_template('seasons.html', seasons=seasons)

@views.route('/team-details/<team_id>', methods=['GET'])
@login_required
def team_details(team_id):
    """
    This view displays information about a specific team, including matches, appearances, and standings.
    """
    team_info = {}
    matches = []
    appearances = []
    standings = []

    mysql_engine = current_app.mysql_engine
    with mysql_engine.connect() as connection:
        # Get team information
        query = "SELECT * FROM teams WHERE team_id = :team_id"
        result = connection.execute(text(query), {'team_id': team_id})
        team_info = result.fetchone()

        # Get matches where this team played (as home or away)
        match_query = """
        SELECT m.match_id, m.match_name, t1.team_name AS home_team, t2.team_name AS away_team, m.score
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE m.home_team_id = :team_id OR m.away_team_id = :team_id
        ORDER BY m.match_id DESC
        """
        result = connection.execute(text(match_query), {'team_id': team_id})
        matches = result.fetchall()

        # Get appearances of this team in matches
        appearance_query = """
        SELECT a.match_id, m.match_name, a.goals_for, a.goals_against
        FROM appearances a
        JOIN matches m ON a.match_id = m.match_id
        WHERE a.team_id = :team_id
        """
        result = connection.execute(text(appearance_query), {'team_id': team_id})
        appearances = result.fetchall()

        # Get the team's standings history
        standings_query = "SELECT s.season_id, s.position, s.points FROM standings s WHERE s.team_id = :team_id"
        result = connection.execute(text(standings_query), {'team_id': team_id})
        standings = result.fetchall()

    return render_template("team_details.html", team=team_info, matches=matches, appearances=appearances, standings=standings)

@views.route('/season/<season_id>', methods=['GET'])
@login_required
def season_overview(season_id):
    season_info, matches, standings = {}, [], []

    mysql_engine = current_app.mysql_engine

    with mysql_engine.connect() as connection:
        # Season Info
        query = "SELECT * FROM seasons WHERE season_id = :season_id"
        result = connection.execute(text(query), {'season_id': season_id})
        season_info = result.fetchone()

        # Matches
        query = """
        SELECT m.match_id, m.match_name, t1.team_name AS home_team, t2.team_name AS away_team, m.score
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE m.season_id = :season_id
        """
        result = connection.execute(text(query), {'season_id': season_id})
        matches = result.fetchall()

        # Standings
        query = """
        SELECT s.position, s.team_id, t.team_name, s.points
        FROM standings s
        JOIN teams t ON s.team_id = t.team_id
        WHERE s.season_id = :season_id
        """
        result = connection.execute(text(query), {'season_id': season_id})
        standings = result.fetchall()

    return render_template("season_overview.html", season=season_info, matches=matches, standings=standings)

@views.route('/match-details/<match_id>', methods=['GET'])
@login_required
def match_details(match_id):
    match_info, appearances = {}, []

    mysql_engine = current_app.mysql_engine

    with mysql_engine.connect() as connection:
        query = """
        SELECT m.match_id, m.match_name, t1.team_name AS home_team, t2.team_name AS away_team, m.score
        FROM matches m
        JOIN teams t1 ON m.home_team_id = t1.team_id
        JOIN teams t2 ON m.away_team_id = t2.team_id
        WHERE m.match_id = :match_id
        """
        result = connection.execute(text(query), {'match_id': match_id})
        match_info = result.fetchone()

        query = """
        SELECT a.team_id, t.team_name, a.goals_for, a.goals_against
        FROM appearances a
        JOIN teams t ON a.team_id = t.team_id
        WHERE a.match_id = :match_id
        """
        result = connection.execute(text(query), {'match_id': match_id})
        appearances = result.fetchall()

    return render_template("match_details.html", match=match_info, appearances=appearances)

