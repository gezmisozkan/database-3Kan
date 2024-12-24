import mysql.connector
from flask import Blueprint, render_template, request, g, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.build_database import Config

views = Blueprint('views', __name__)

@views.before_app_request
def connect_to_database():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )

@views.teardown_request
def close_database_connection(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@views.route("/")
def home():
    """
    Renders the home page for the football database.
    """
    return render_template("home.html")  # homepage template is named 'home.html'

@views.before_app_request
def load_recent_seasons():
    """
    This function loads the 5 most recent unique years to be displayed in the navbar.
    """
    try:
        cursor = g.db.cursor()
        recent_years_query = "SELECT DISTINCT season FROM seasons ORDER BY season DESC LIMIT 5"
        cursor.execute(recent_years_query)
        g.recent_seasons = [row[0] for row in cursor.fetchall()]  # Ensure this is working
    except mysql.connector.Error as e:
        print(f"MySQL error occurred: {e}")
    finally:
        cursor.close()
        
@views.route('/seasons/<year>', methods=['GET'])
def season_tiers(year):
    """
    This view displays all available tiers for the selected season year.
    """
    try:
        cursor = g.db.cursor(dictionary=True)  # Use a dictionary cursor to access columns by name
        tier_query = """
            SELECT season_id, tier 
            FROM seasons 
            WHERE season = %s 
            ORDER BY tier
        """
        cursor.execute(tier_query, (year,))  # Execute query with parameter
        tiers = cursor.fetchall()  # Fetch all results
        print("Tiers for Season", year, ":", tiers)  # Debug Print
    except mysql.connector.Error as e:
        print(f"MySQL error occurred: {e}")
        return "Database error occurred.", 500
    finally:
        cursor.close()  # Close the cursor after execution

    return render_template("season_tiers.html", year=year, tiers=tiers)



@views.route('/teams', methods=['GET'])
def teams():
    teams = []
    search_query = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    try:
        cursor = g.db.cursor(dictionary=True)
        
        if search_query:
            count_query = "SELECT COUNT(*) as total FROM teams WHERE team_name LIKE %s"
            cursor.execute(count_query, (f'%{search_query}%',))
        else:
            count_query = "SELECT COUNT(*) as total FROM teams"
            cursor.execute(count_query)
        
        total_results = cursor.fetchone()['total']
        total_pages = (total_results // per_page) + (1 if total_results % per_page > 0 else 0)

        if search_query:
            team_query = """
                SELECT team_id, team_name 
                FROM teams 
                WHERE team_name LIKE %s 
                ORDER BY team_name 
                LIMIT %s OFFSET %s
            """
            cursor.execute(team_query, (f'%{search_query}%', per_page, offset))
        else:
            team_query = """
                SELECT team_id, team_name 
                FROM teams 
                ORDER BY team_name 
                LIMIT %s OFFSET %s
            """
            cursor.execute(team_query, (per_page, offset))

        teams = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"MySQL error occurred: {e}")
    finally:
        cursor.close()

    return render_template("teams.html", teams=teams, search_query=search_query, page=page, total_pages=total_pages)

@views.route('/matches', methods=['GET', 'POST'])
def matches():
    teams, matches, selected_team = [], [], None
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    try:
        cursor = g.db.cursor(dictionary=True)

        query = "SELECT DISTINCT home_team_name FROM matches"
        cursor.execute(query)
        teams = [row['home_team_name'] for row in cursor.fetchall()]

        # Handle form submission and query parameters for selected team
        if request.method == 'POST':
            selected_team = request.form['team']
        else:
            selected_team = request.args.get('selected_team')
        total_pages = 0
        if selected_team:
            count_query = """
                SELECT COUNT(*) as total 
                FROM matches 
                WHERE home_team_name = %s OR away_team_name = %s
            """
            cursor.execute(count_query, (selected_team, selected_team))
            total_results = cursor.fetchone()['total']
            total_pages = (total_results // per_page) + (1 if total_results % per_page > 0 else 0)

            # Get match details and team IDs
            match_query = """
                SELECT 
                    m.match_id, 
                    m.match_name,
                    m.home_team_name, 
                    m.away_team_name, 
                    t1.team_id AS home_team_id, 
                    t2.team_id AS away_team_id, 
                    m.home_team_score, 
                    m.away_team_score
                FROM matches m
                JOIN teams t1 ON m.home_team_name = t1.team_name 
                JOIN teams t2 ON m.away_team_name = t2.team_name 
                WHERE m.home_team_name = %s OR m.away_team_name = %s
                ORDER BY m.match_id DESC 
                LIMIT %s OFFSET %s
            """
            cursor.execute(match_query, (selected_team, selected_team, per_page, offset))
            matches = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"MySQL error occurred: {e}")
    finally:
        cursor.close()

    return render_template("matches.html", teams=teams, matches=matches, selected_team=selected_team, page=page, total_pages=total_pages)


@views.route('/seasons', methods=['GET'])
def search_seasons():
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    # Capture the sorting column and order
    sort = request.args.get('sort', 'season_id')
    order = request.args.get('order', 'asc')

    # Sanitize/validate sort and order, so we don't allow invalid column or injection
    valid_columns = {'key_id', 'season_id', 'season', 'tier', 'division', 'subdivision', 'winner', 'count_teams'}
    if sort not in valid_columns:
        sort = 'season_id'
    if order not in ['asc', 'desc']:
        order = 'asc'

    season = request.args.get('season')
    tier = request.args.get('tier')
    division = request.args.get('division')

    try:
        cursor = g.db.cursor(dictionary=True)

        # Get total count (for pagination)
        count_query = "SELECT COUNT(*) as total FROM seasons"
        cursor.execute(count_query)
        total_results = cursor.fetchone()['total']
        total_pages = (total_results // per_page) + (1 if total_results % per_page > 0 else 0)

        # Build the main query
        query = """
        SELECT key_id, season_id, season, tier, division, subdivision, winner, count_teams
        FROM seasons
        WHERE 1=1
        """
        params = []

        if season:
            query += " AND season = %s"
            params.append(season)
        if tier:
            query += " AND tier = %s"
            params.append(tier)
        if division:
            query += " AND division = %s"
            params.append(division)

        # Add sorting and pagination
        query += f" ORDER BY {sort} {order} LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cursor.execute(query, params)
        seasons = cursor.fetchall()

    except mysql.connector.Error as e:
        print(f"MySQL error occurred: {e}")
        seasons = []
        total_pages = 1
    finally:
        cursor.close()

    return render_template(
        'seasons.html',
        seasons=seasons,
        page=page,
        total_pages=total_pages,
        sort=sort,
        order=order,
        season=season,
        tier=tier,
        division=division
    )

@views.route('/team-details/<team_id>', methods=['GET', 'POST'])
def team_details(team_id):
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need to be logged in to post a comment.', 'error')
            return redirect(url_for('views.team_details', team_id=team_id))

        comment_text = request.form.get('comment')
        if not comment_text:
            flash('Comment cannot be empty.', 'error')
            return redirect(url_for('views.team_details', team_id=team_id))

        try:
            cursor = g.db.cursor()
            cursor.execute("""
                INSERT INTO team_comments (team_id, user_id, comment)
                VALUES (%s, %s, %s)
            """, (team_id, current_user.id, comment_text))
            g.db.commit()
            flash('Comment posted successfully!', 'success')
        except mysql.connector.Error as e:
            flash(f'An error occurred while posting the comment: {e}', 'error')
        finally:
            cursor.close()

    try:
        cursor = g.db.cursor(dictionary=True)
        
        # Fetch total number of matches for pagination
        count_query = "SELECT COUNT(*) as total FROM matches WHERE home_team_id = %s OR away_team_id = %s"
        cursor.execute(count_query, (team_id, team_id))
        total_results = cursor.fetchone()['total']
        total_pages = (total_results // per_page) + (1 if total_results % per_page > 0 else 0)

        # Fetch team details
        query = "SELECT * FROM teams WHERE team_id = %s"
        cursor.execute(query, (team_id,))
        team_info = cursor.fetchone()

        # Fetch recent matches with pagination
        match_query = """
            SELECT 
                m.match_id, m.match_name, t1.team_name AS home_team, t2.team_name AS away_team, t1.team_id AS home_team_id, t2.team_id AS away_team_id, m.score
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.team_id
            JOIN teams t2 ON m.away_team_id = t2.team_id
            WHERE m.home_team_id = %s OR m.away_team_id = %s
            ORDER BY m.match_id DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(match_query, (team_id, team_id, per_page, offset))
        matches = cursor.fetchall()

        # Fetch comments
        cursor.execute("""
            SELECT c.comment, c.created_at, u.full_name AS username
            FROM team_comments c
            JOIN User u ON c.user_id = u.id
            WHERE c.team_id = %s
            ORDER BY c.created_at DESC
        """, (team_id,))
        comments = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'An error occurred while fetching team details: {e}', 'error')
        team_info = {}
        matches = []
        comments = []
        total_pages = 1
    finally:
        cursor.close()

    return render_template(
        "team_details.html", 
        team=team_info, 
        matches=matches, 
        comments=comments, 
        page=page, 
        total_pages=total_pages
    )


@views.route('/season/<season_id>', methods=['GET'])
def season_overview(season_id):
    try:
        cursor = g.db.cursor(dictionary=True)
        
        query = "SELECT * FROM seasons WHERE season_id = %s"
        cursor.execute(query, (season_id,))
        season_info = cursor.fetchone()

        match_query = """
            SELECT m.match_id, m.match_name, t1.team_name AS home_team, t2.team_name AS away_team, m.score
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.team_id
            JOIN teams t2 ON m.away_team_id = t2.team_id
            WHERE m.season_id = %s
        """
        cursor.execute(match_query, (season_id,))
        matches = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"MySQL error occurred: {e}")
    finally:
        cursor.close()

    return render_template("season_overview.html", season=season_info, matches=matches)

@views.route('/delete-team/<team_id>', methods=['POST'])
@login_required
def delete_team(team_id):
    if current_user.role != 'admin':
        flash('Only admins can delete teams.', 'error')
        return redirect(url_for('views.teams'))
    
    try:
        cursor = g.db.cursor()
        cursor.execute("DELETE FROM teams WHERE team_id = %s", (team_id,))
        g.db.commit()
        flash(f'Team deleted successfully!', 'success')
    except mysql.connector.Error as e:
        flash(f'Failed to delete team: {e}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('views.teams'))

@views.route('/delete-match/<match_id>', methods=['POST'])
@login_required
def delete_match(match_id):
    """
    Route to delete a match from the database.
    The user is redirected back to the current page for the selected team.
    """
    if current_user.role != 'admin':
        flash('Only admins can delete matches.', 'error')
        return redirect(url_for('views.matches'))

    page = request.form.get('page', 1)
    selected_team = request.form.get('selected_team')

    try:
        cursor = g.db.cursor()
        
        # Delete the match from the Matches table
        cursor.execute("DELETE FROM Matches WHERE match_id = %s", (match_id,))
        g.db.commit()
        
        flash(f'Match {match_id} deleted successfully!', 'success')
    except mysql.connector.Error as e:
        flash(f'An error occurred while deleting match {match_id}: {e}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('views.matches', page=page, selected_team=selected_team))


@views.route('/admin', methods=['GET'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Only admins can access the admin panel.', 'error')
        return redirect(url_for('views.home'))
    
    return render_template('admin.html')

@views.route('/delete-season/<season_id>', methods=['POST'])
@login_required
def delete_season(season_id):
    """
    Route to delete a season from the database.
    Only admin users can delete a season.
    """
    if current_user.role != 'admin':
        flash('Only admins can delete seasons.', 'error')
        return redirect(url_for('views.search_seasons'))

    try:
        cursor = g.db.cursor()
        
        # Delete the season from the Seasons table
        cursor.execute("DELETE FROM Seasons WHERE season_id = %s", (season_id,))
        g.db.commit()
        
        flash(f'Season {season_id} deleted successfully!', 'success')
    except mysql.connector.Error as e:
        flash(f'An error occurred while deleting season {season_id}: {e}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('views.search_seasons'))


@views.route('/standings', methods=['GET'])
def standings():
    """
    Route to display the standings with optional searching and sorting.
    """
    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page

    # New: Sort parameters
    sort_by = request.args.get('sort_by', 'season')  # default sort by season
    sort_order = request.args.get('sort_order', 'asc')  # default ascending
    valid_sort_columns = ['season', 'tier', 'division', 'team_name', 'position']

    # Validate columns
    if sort_by not in valid_sort_columns:
        sort_by = 'season'

    # Validate sort order
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'

    try:
        cursor = g.db.cursor(dictionary=True)

        # Build the query with search and sorting
        # IMPORTANT: Use placeholders only for user-submitted *values*, not columns
        query = f"""
            SELECT * 
            FROM standings 
            WHERE team_name LIKE %s
               OR season LIKE %s
               OR division LIKE %s
            ORDER BY {sort_by} {sort_order}
        """

        cursor.execute(query, (
            f"%{search_query}%",
            f"%{search_query}%",
            f"%{search_query}%"
        ))
        standings = cursor.fetchall()

        # Pagination logic
        total_items = len(standings)
        total_pages = (total_items + per_page - 1) // per_page

        # Slice the data for the page
        standings = standings[(page - 1) * per_page: page * per_page]

    except mysql.connector.Error as e:
        flash(f'An error occurred while fetching standings: {e}', 'error')
        standings = []
        total_pages = 1
    finally:
        cursor.close()

    return render_template(
        'standings.html',
        standings=standings,
        search_query=search_query,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        sort_order=sort_order,
        max=max,
        min=min
    )


@views.route('/standing-details/<key_id>', methods=['GET'])
def standing_details(key_id):
    """
    Route to display the details of a specific standing.
    """
    try:
        cursor = g.db.cursor(dictionary=True)
        
        # Query to fetch the standing details
        query = "SELECT * FROM standings WHERE key_id = %s"
        cursor.execute(query, (key_id,))
        standing = cursor.fetchone()
        
        if not standing:
            flash(f'Standing with key_id {key_id} not found.', 'error')
            return redirect(url_for('views.standings'))
        
    except mysql.connector.Error as e:
        flash(f'An error occurred while fetching standing details: {e}', 'error')
        return redirect(url_for('views.standings'))
    finally:
        cursor.close()

    return render_template("standing_details.html", standing=standing)

@views.route('/delete_standing/<key_id>', methods=['POST'])
@login_required
def delete_standing(key_id):
    """
    Route to delete a standing from the database.
    Only admin users can delete a standing.
    """
    if current_user.role != 'admin':
        flash('Only admins can delete standings.', 'error')
        return redirect(url_for('views.standings'))

    try:
        cursor = g.db.cursor()
        
        # Delete the standing from the standings table
        cursor.execute("DELETE FROM standings WHERE key_id = %s", (key_id,))
        g.db.commit()
        
        flash(f'Standing {key_id} deleted successfully!', 'success')
    except mysql.connector.Error as e:
        flash(f'An error occurred while deleting standing {key_id}: {e}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('views.standings'))

@views.route('/match-details/<match_id>', methods=['GET', 'POST'])
def match_details(match_id):
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('You need to be logged in to post a comment.', 'error')
            return redirect(url_for('views.match_details', match_id=match_id))

        comment_text = request.form.get('comment')
        if not comment_text:
            flash('Comment cannot be empty.', 'error')
            return redirect(url_for('views.match_details', match_id=match_id))

        try:
            cursor = g.db.cursor()
            cursor.execute("""
                INSERT INTO comments (match_id, user_id, comment)
                VALUES (%s, %s, %s)
            """, (match_id, current_user.id, comment_text))
            g.db.commit()
            flash('Comment posted successfully!', 'success')
        except mysql.connector.Error as e:
            flash(f'An error occurred while posting the comment: {e}', 'error')
        finally:
            cursor.close()

    try:
        cursor = g.db.cursor(dictionary=True)
        
        # Fetch match details
        query = """
            SELECT 
                m.match_id, m.match_name, t1.team_name AS home_team, t2.team_name AS away_team, t1.team_id AS home_team_id, t2.team_id AS away_team_id, m.score
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.team_id
            JOIN teams t2 ON m.away_team_id = t2.team_id
            WHERE m.match_id = %s
        """
        cursor.execute(query, (match_id,))
        match_info = cursor.fetchone()  # Use fetchone() for single row
        print("Match Info:", match_info)  # Debug print

        # Fetch comments
        cursor.execute("""
            SELECT c.comment, c.created_at, u.full_name AS username
            FROM comments c
            JOIN User u ON c.user_id = u.id
            WHERE c.match_id = %s
            ORDER BY c.created_at DESC
        """, (match_id,))
        comments = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'An error occurred while fetching match details: {e}', 'error')
        match_info = {}
        comments = []
    finally:
        cursor.close()

    return render_template("match_details.html", match=match_info, comments=comments)


@views.route('/comments', methods=['GET'])
@login_required
def user_comments():
    try:
        cursor = g.db.cursor(dictionary=True)
        
        # Fetch user's match comments
        cursor.execute("""
            SELECT c.comment, c.created_at, m.match_name
            FROM comments c
            JOIN matches m ON c.match_id = m.match_id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
        """, (current_user.id,))
        match_comments = cursor.fetchall()

        # Fetch user's team comments
        cursor.execute("""
            SELECT c.comment, c.created_at, t.team_name
            FROM team_comments c
            JOIN teams t ON c.team_id = t.team_id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
        """, (current_user.id,))
        team_comments = cursor.fetchall()
    except mysql.connector.Error as e:
        flash(f'An error occurred while fetching comments: {e}', 'error')
        match_comments = []
        team_comments = []
    finally:
        cursor.close()

    return render_template("comments.html", match_comments=match_comments, team_comments=team_comments)