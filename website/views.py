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

@views.route('/matches', methods=['GET'])
def matches():
    teams, matches, selected_team, search_query, sort, order = [], [], None, None, None, None
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    try:
        cursor = g.db.cursor(dictionary=True)

        # Fetch distinct home team names for dropdown
        team_query = "SELECT DISTINCT home_team_name FROM matches"
        cursor.execute(team_query)
        teams = [row['home_team_name'] for row in cursor.fetchall()]

        # Get search and sort parameters
        selected_team = request.args.get('team', None)
        search_query = request.args.get('search', '').strip()
        sort = request.args.get('sort', 'match_id')  # Default sorting by match_id
        order = request.args.get('order', 'asc')  # Default order is ascending

        # Build base query for matches
        base_query = """
            SELECT 
                m.match_id, 
                m.match_name,
                m.home_team_name, 
                m.away_team_name, 
                t1.team_id AS home_team_id, 
                t2.team_id AS away_team_id, 
                m.home_team_score, 
                m.away_team_score,
                s.season AS season_year,
                s.tier AS season_tier,
                s.season_id
            FROM matches m
            JOIN teams t1 ON m.home_team_name = t1.team_name 
            JOIN teams t2 ON m.away_team_name = t2.team_name
            LEFT JOIN seasons s ON m.season_id = s.season_id
            WHERE 1=1 # Placeholder for additional filters
        """

        # Add filters based on search inputs
        filters = []
        params = []
        if selected_team:
            filters.append("(m.home_team_name = %s OR m.away_team_name = %s)")
            params.extend([selected_team, selected_team])
        if search_query:
            filters.append("m.match_name LIKE %s")
            params.append(f"%{search_query}%")

        # Combine filters into the base query
        if filters:
            base_query += " AND " + " AND ".join(filters)

        # Add sorting and pagination
        base_query += f" ORDER BY {sort} {order} LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        # Execute query and fetch results
        cursor.execute(base_query, params)
        matches = cursor.fetchall()

        # Count total results for pagination
        count_query = "SELECT COUNT(*) as total FROM matches m WHERE 1=1"
        if filters:
            count_query += " AND " + " AND ".join(filters)
        cursor.execute(count_query, params[:-2])  # Exclude LIMIT and OFFSET from params
        total_results = cursor.fetchone()['total']
        total_pages = (total_results // per_page) + (1 if total_results % per_page > 0 else 0)

    except mysql.connector.Error as e:
        print(f"MySQL error occurred: {e}")
    finally:
        cursor.close()

    return render_template(
        "matches.html", 
        teams=teams, 
        matches=matches, 
        selected_team=selected_team, 
        search_query=search_query, 
        sort=sort, 
        order=order, 
        page=page, 
        total_pages=total_pages
    )


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
        team_query = "SELECT * FROM teams WHERE team_id = %s"
        cursor.execute(team_query, (team_id,))
        team_info = cursor.fetchone()

        # Fetch recent matches with season info
        match_query = """
            SELECT 
                m.match_id, 
                m.match_name, 
                t1.team_name AS home_team, 
                t2.team_name AS away_team, 
                t1.team_id AS home_team_id, 
                t2.team_id AS away_team_id, 
                m.score,
                s.season AS season_year,
                s.tier AS season_tier
            FROM matches m
            JOIN teams t1 ON m.home_team_id = t1.team_id
            JOIN teams t2 ON m.away_team_id = t2.team_id
            LEFT JOIN seasons s ON m.season_id = s.season_id
            WHERE m.home_team_id = %s OR m.away_team_id = %s
            ORDER BY m.match_id DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(match_query, (team_id, team_id, per_page, offset))
        matches = cursor.fetchall()

        # Fetch comments
        comment_query = """
            SELECT c.comment, c.created_at, u.full_name AS username
            FROM team_comments c
            JOIN User u ON c.user_id = u.id
            WHERE c.team_id = %s
            ORDER BY c.created_at DESC
        """
        cursor.execute(comment_query, (team_id,))
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

    except mysql.connector.Error as e:
        print(f"MySQL error occurred: {e}")
    finally:
        cursor.close()

    return render_template("season_overview.html", season=season_info)

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

@views.route('/admin/comments', methods=['GET'])
@login_required
def admin_comments():
    if current_user.role != 'admin':
        flash('Only admins can access this page.', 'error')
        return redirect(url_for('views.home'))

    # Pagination setup
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    try:
        cursor = g.db.cursor(dictionary=True)

        # Fetch total match comments for pagination
        match_count_query = "SELECT COUNT(*) AS total FROM comments"
        cursor.execute(match_count_query)
        match_total = cursor.fetchone()['total']

        # Fetch match comments (paginated)
        match_query = """
            SELECT 
                c.comment_id, 
                c.comment, 
                c.created_at, 
                m.match_name, 
                u.full_name AS user_name,
                u.id AS user_id
            FROM comments c
            JOIN matches m ON c.match_id = m.match_id
            JOIN User u ON c.user_id = u.id
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(match_query, (per_page, offset))
        match_comments = cursor.fetchall()

        # Group match comments by user
        grouped_match_comments = {}
        for comment in match_comments:
            user_id = comment['user_id']
            user_name = comment['user_name']
            if user_id not in grouped_match_comments:
                grouped_match_comments[user_id] = {
                    'user_name': user_name,
                    'comments': []
                }
            grouped_match_comments[user_id]['comments'].append(comment)

        # Fetch total team comments for pagination
        team_count_query = "SELECT COUNT(*) AS total FROM team_comments"
        cursor.execute(team_count_query)
        team_total = cursor.fetchone()['total']

        # Fetch team comments (paginated)
        team_query = """
            SELECT 
                c.comment_id, 
                c.comment, 
                c.created_at, 
                t.team_name, 
                u.full_name AS user_name,
                u.id AS user_id
            FROM team_comments c
            JOIN teams t ON c.team_id = t.team_id
            JOIN User u ON c.user_id = u.id
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(team_query, (per_page, offset))
        team_comments = cursor.fetchall()

        # Group team comments by user
        grouped_team_comments = {}
        for comment in team_comments:
            user_id = comment['user_id']
            user_name = comment['user_name']
            if user_id not in grouped_team_comments:
                grouped_team_comments[user_id] = {
                    'user_name': user_name,
                    'comments': []
                }
            grouped_team_comments[user_id]['comments'].append(comment)

        # Calculate total pages (optional: based on combined or individual totals)
        total_pages = max(
            (match_total + per_page - 1) // per_page,
            (team_total + per_page - 1) // per_page
        )

    except mysql.connector.Error as e:
        flash(f"Error fetching comments: {e}", "error")
        grouped_match_comments, grouped_team_comments, total_pages = {}, {}, 1
    finally:
        cursor.close()

    return render_template(
        'admin_comments.html',
        match_comments=grouped_match_comments.values(),
        team_comments=grouped_team_comments.values(),
        page=page,
        total_pages=total_pages
    )


@views.route('/admin/comments/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_match_comment(comment_id):
    if current_user.role != 'admin':
        flash('Only admins can delete comments.', 'error')
        return redirect(url_for('views.admin_comments'))

    try:
        cursor = g.db.cursor()
        query = "DELETE FROM comments WHERE comment_id = %s"
        cursor.execute(query, (comment_id,))
        g.db.commit()
        flash('Match comment deleted successfully.', 'success')
    except mysql.connector.Error as e:
        flash(f"Error deleting match comment: {e}", "error")
    finally:
        cursor.close()

    return redirect(url_for('views.admin_comments'))

@views.route('/admin/team-comments/delete/<int:comment_id>', methods=['POST'])
@login_required
def delete_team_comment(comment_id):
    if current_user.role != 'admin':
        flash('Only admins can delete comments.', 'error')
        return redirect(url_for('views.admin_comments'))

    try:
        cursor = g.db.cursor()
        query = "DELETE FROM team_comments WHERE comment_id = %s"
        cursor.execute(query, (comment_id,))
        g.db.commit()
        flash('Team comment deleted successfully.', 'success')
    except mysql.connector.Error as e:
        flash(f"Error deleting team comment: {e}", "error")
    finally:
        cursor.close()

    return redirect(url_for('views.admin_comments'))


@views.route('/standings_insert')
@login_required
def standings_insert():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('views.standings'))
    return render_template('standings_insert.html')

@views.route('/insert_standing', methods=['POST'])
@login_required
def insert_standing():
    if current_user.role != 'admin':
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('views.standings'))

    season_data = {
        'season_id': request.form.get('season_id'),
        'season': request.form.get('season'),
        'tier': request.form.get('tier'),
        'division': request.form.get('division'),
        'subdivision': request.form.get('subdivision', 'None')
    }

    team_data = {
        'team_id': request.form.get('team_id'),
        'team_name': request.form.get('team_name'),
        'current': True,
        'former': False,
        'defunct': False,
        'first_appearance': request.form.get('season')
    }

    standing_data = {
        'season_id': request.form.get('season_id'),
        'season': request.form.get('season'),
        'tier': request.form.get('tier'),
        'division': request.form.get('division'),
        'subdivision': request.form.get('subdivision', 'None'),
        'position': request.form.get('position'),
        'team_id': request.form.get('team_id'),
        'team_name': request.form.get('team_name'),
        'played': request.form.get('played'),
        'wins': request.form.get('wins'),
        'draws': request.form.get('draws'),
        'losses': request.form.get('losses'),
        'goals_for': request.form.get('goals_for'),
        'goals_against': request.form.get('goals_against'),
        'goal_difference': request.form.get('goal_difference'),
        'points': request.form.get('points'),
        'point_adjustment': request.form.get('point_adjustment', 0)
    }

    try:
        cursor = g.db.cursor()

        # Insert into seasons table if season_id does not exist
        cursor.execute("SELECT COUNT(*) FROM seasons WHERE season_id = %s", (season_data['season_id'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO seasons (season_id, season, tier, division, subdivision)
                VALUES (%(season_id)s, %(season)s, %(tier)s, %(division)s, %(subdivision)s)
            """, season_data)

        # Insert into teams table if team_id does not exist
        cursor.execute("SELECT COUNT(*) FROM teams WHERE team_id = %s", (team_data['team_id'],))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO teams (team_id, team_name, current, former, defunct, first_appearance)
                VALUES (%(team_id)s, %(team_name)s, %(current)s, %(former)s, %(defunct)s, %(first_appearance)s)
            """, team_data)

        # Insert into standings table
        cursor.execute("""
            INSERT INTO standings (season_id, season, tier, division, subdivision, position, team_id, team_name, played, wins, draws, losses, goals_for, goals_against, goal_difference, points, point_adjustment)
            VALUES (%(season_id)s, %(season)s, %(tier)s, %(division)s, %(subdivision)s, %(position)s, %(team_id)s, %(team_name)s, %(played)s, %(wins)s, %(draws)s, %(losses)s, %(goals_for)s, %(goals_against)s, %(goal_difference)s, %(points)s, %(point_adjustment)s)
        """, standing_data)

        g.db.commit()
        flash('Team data inserted successfully!', 'success')
    except mysql.connector.Error as e:
        g.db.rollback()
        flash(f'An error occurred: {e}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('views.standings'))

def get_season_ids():
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT season_id FROM seasons")
        seasons = [row['season_id'] for row in cursor.fetchall()]
        return seasons
    except mysql.connector.Error:
        return []
    finally:
        cursor.close()


def get_team_names():
    try:
        cursor = g.db.cursor(dictionary=True)
        cursor.execute("SELECT team_name FROM teams")
        teams = [row['team_name'] for row in cursor.fetchall()]
        return teams
    except mysql.connector.Error:
        return []
    finally:
        cursor.close()

@views.route('/insert-match', methods=['GET', 'POST'])
@login_required
def insert_match():
    if current_user.role != 'admin':
        flash('Only admins can insert matches.', 'error')
        return redirect(url_for('views.matches'))

    if request.method == 'POST':
        season_id = request.form.get('season_id')
        home_team_name = request.form.get('home_team_name')
        away_team_name = request.form.get('away_team_name')
        home_team_score = request.form.get('home_team_score', '')
        away_team_score = request.form.get('away_team_score', '')

        try:
            cursor = g.db.cursor(dictionary=True)

            # Fetch team IDs based on team names
            cursor.execute("SELECT team_id FROM teams WHERE team_name = %s", (home_team_name,))
            home_team_id = cursor.fetchone()['team_id']

            cursor.execute("SELECT team_id FROM teams WHERE team_name = %s", (away_team_name,))
            away_team_id = cursor.fetchone()['team_id']

            # Restrict same team IDs
            if home_team_id == away_team_id:
                flash("Home and away teams cannot be the same.", "error")
                return render_template(
                    'insert_match.html',
                    seasons=get_season_ids(),
                    teams=get_team_names(),
                    selected_season=season_id,
                    selected_home_team=home_team_name,
                    selected_away_team=away_team_name,
                    home_team_score=home_team_score,
                    away_team_score=away_team_score,
                )

            # Fetch season details
            cursor.execute("SELECT season, tier, division, subdivision FROM seasons WHERE season_id = %s", (season_id,))
            season_info = cursor.fetchone()

            # Calculate the next match ID for the season
            cursor.execute("SELECT COUNT(*) AS total_matches FROM matches WHERE season_id = %s", (season_id,))
            total_matches = cursor.fetchone()['total_matches']
            match_id = f"M-{season_id}-{total_matches + 1:03d}"

            # Generate match_name
            match_name = f"{home_team_name} vs {away_team_name}"

            # Calculate result and margins
            home_team_score_margin = int(home_team_score) - int(away_team_score)
            away_team_score_margin = int(away_team_score) - int(home_team_score)
            result = (
                'draw' if home_team_score == away_team_score else
                'home team win' if int(home_team_score) > int(away_team_score) else
                'away team win'
            )
            home_team_win = int(int(home_team_score) > int(away_team_score))
            away_team_win = int(int(away_team_score) > int(home_team_score))
            draw = int(int(home_team_score) == int(away_team_score))

            # Generate key_id
            cursor.execute("SELECT IFNULL(MAX(key_id), 0) + 1 AS next_key_id FROM matches")
            key_id = cursor.fetchone()['next_key_id']

            # Insert match into the database
            insert_query = """
                INSERT INTO matches (
                    key_id, season_id, season, tier, division, subdivision, match_id, match_name,
                    home_team_id, home_team_name, away_team_id, away_team_name, score,
                    home_team_score, away_team_score, home_team_score_margin, away_team_score_margin,
                    result, home_team_win, away_team_win, draw
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            cursor.execute(insert_query, (
                key_id, season_id, season_info['season'], season_info['tier'], season_info['division'],
                season_info['subdivision'], match_id, match_name, home_team_id, home_team_name,
                away_team_id, away_team_name, f"{home_team_score}-{away_team_score}",
                int(home_team_score), int(away_team_score), home_team_score_margin,
                away_team_score_margin, result, home_team_win, away_team_win, draw
            ))
            g.db.commit()
            flash('Match inserted successfully!', 'success')
        except mysql.connector.Error as e:
            g.db.rollback()
            flash(f'Error inserting match: {e}', 'error')
        finally:
            cursor.close()
        return redirect(url_for('views.matches'))

    return render_template(
        'insert_match.html',
        seasons=get_season_ids(),
        teams=get_team_names(),
    )



@views.route('/fetch-season-info/<season_id>', methods=['GET'])
@login_required
def fetch_season_info(season_id):
    try:
        cursor = g.db.cursor(dictionary=True)
        query = """
            SELECT season AS year, tier, division, subdivision
            FROM seasons
            WHERE season_id = %s
        """
        cursor.execute(query, (season_id,))
        season_info = cursor.fetchone()
        if season_info:
            return season_info, 200
        else:
            return {"error": "Season not found"}, 404
    except mysql.connector.Error as e:
        return {"error": str(e)}, 500
    finally:
        cursor.close()



@views.route('/update-match/<match_id>', methods=['GET', 'POST'])
@login_required
def update_match(match_id):
    if current_user.role != 'admin':
        flash('Only admins can update matches.', 'error')
        return redirect(url_for('views.matches'))
    
    if request.method == 'POST':
        home_team_score = request.form.get('home_team_score')
        away_team_score = request.form.get('away_team_score')

        # Validate inputs to ensure non-negative numbers
        try:
            home_team_score = int(home_team_score)
            away_team_score = int(away_team_score)

            if home_team_score < 0 or away_team_score < 0:
                flash('Scores cannot be negative.', 'error')
                return redirect(url_for('views.update_match', match_id=match_id))
        except ValueError:
            flash('Scores must be valid numbers.', 'error')
            return redirect(url_for('views.update_match', match_id=match_id))

        try:
            cursor = g.db.cursor()
            query = """
                UPDATE matches
                SET home_team_score = %s, away_team_score = %s
                WHERE match_id = %s
            """
            cursor.execute(query, (home_team_score, away_team_score, match_id))
            g.db.commit()
            flash('Match updated successfully!', 'success')
        except mysql.connector.Error as e:
            g.db.rollback()
            flash(f'Error updating match: {e}', 'error')
        finally:
            cursor.close()
        return redirect(url_for('views.matches'))

    # Fetch match details for prefilling the form
    try:
        cursor = g.db.cursor(dictionary=True)
        query = "SELECT * FROM matches WHERE match_id = %s"
        cursor.execute(query, (match_id,))
        match = cursor.fetchone()
    except mysql.connector.Error as e:
        flash(f'Error fetching match details: {e}', 'error')
        return redirect(url_for('views.matches'))
    finally:
        cursor.close()

    return render_template('update_match.html', match=match)

