import mysql.connector
from mysql.connector import Error
from build_database import Config

# Database connection details
DB_HOST = Config.DB_HOST
DB_USER = Config.DB_USER
DB_PASSWORD = Config.DB_PASSWORD
DB_NAME = Config.DB_NAME

# Trigger creation statements
trigger_after_insert = """
CREATE TRIGGER after_match_insert
AFTER INSERT ON matches
FOR EACH ROW
BEGIN
    -- Update home team standings
    UPDATE standings
    SET 
        played = played + 1,
        wins = wins + (NEW.home_team_win),
        losses = losses + (NEW.away_team_win),
        draws = draws + (NEW.draw),
        goals_for = goals_for + NEW.home_team_score,
        goals_against = goals_against + NEW.away_team_score,
        goal_difference = goal_difference + (NEW.home_team_score - NEW.away_team_score),
        points = points + (3 * NEW.home_team_win) + (1 * NEW.draw)
    WHERE team_id = NEW.home_team_id;

    -- Update away team standings
    UPDATE standings
    SET 
        played = played + 1,
        wins = wins + (NEW.away_team_win),
        losses = losses + (NEW.home_team_win),
        draws = draws + (NEW.draw),
        goals_for = goals_for + NEW.away_team_score,
        goals_against = goals_against + NEW.home_team_score,
        goal_difference = goal_difference + (NEW.away_team_score - NEW.home_team_score),
        points = points + (3 * NEW.away_team_win) + (1 * NEW.draw)
    WHERE team_id = NEW.away_team_id;
END;
"""

trigger_after_update = """
CREATE TRIGGER after_match_update
AFTER UPDATE ON matches
FOR EACH ROW
BEGIN
    -- Reverse old values for the home team
    UPDATE standings
    SET 
        played = played - 1,
        wins = wins - (OLD.home_team_win),
        losses = losses - (OLD.away_team_win),
        draws = draws - (OLD.draw),
        goals_for = goals_for - OLD.home_team_score,
        goals_against = goals_against - OLD.away_team_score,
        goal_difference = goal_difference - (OLD.home_team_score - OLD.away_team_score),
        points = points - (3 * OLD.home_team_win) - (1 * OLD.draw)
    WHERE team_id = OLD.home_team_id;

    -- Reverse old values for the away team
    UPDATE standings
    SET 
        played = played - 1,
        wins = wins - (OLD.away_team_win),
        losses = losses - (OLD.home_team_win),
        draws = draws - (OLD.draw),
        goals_for = goals_for - OLD.away_team_score,
        goals_against = goals_against - OLD.home_team_score,
        goal_difference = goal_difference - (OLD.away_team_score - OLD.home_team_score),
        points = points - (3 * OLD.away_team_win) - (1 * OLD.draw)
    WHERE team_id = OLD.away_team_id;

    -- Apply new values for the home team
    UPDATE standings
    SET 
        played = played + 1,
        wins = wins + (NEW.home_team_win),
        losses = losses + (NEW.away_team_win),
        draws = draws + (NEW.draw),
        goals_for = goals_for + NEW.home_team_score,
        goals_against = goals_against + NEW.away_team_score,
        goal_difference = goal_difference + (NEW.home_team_score - NEW.away_team_score),
        points = points + (3 * NEW.home_team_win) + (1 * NEW.draw)
    WHERE team_id = NEW.home_team_id;

    -- Apply new values for the away team
    UPDATE standings
    SET 
        played = played + 1,
        wins = wins + (NEW.away_team_win),
        losses = losses + (NEW.home_team_win),
        draws = draws + (NEW.draw),
        goals_for = goals_for + NEW.away_team_score,
        goals_against = goals_against + NEW.home_team_score,
        goal_difference = goal_difference + (NEW.away_team_score - NEW.home_team_score),
        points = points + (3 * NEW.away_team_win) + (1 * NEW.draw)
    WHERE team_id = NEW.away_team_id;
END;
"""

trigger_after_delete = """
CREATE TRIGGER after_match_delete
AFTER DELETE ON matches
FOR EACH ROW
BEGIN
    -- Reverse home team standings
    UPDATE standings
    SET 
        played = played - 1,
        wins = wins - (OLD.home_team_win),
        losses = losses - (OLD.away_team_win),
        draws = draws - (OLD.draw),
        goals_for = goals_for - OLD.home_team_score,
        goals_against = goals_against - OLD.away_team_score,
        goal_difference = goal_difference - (OLD.home_team_score - OLD.away_team_score),
        points = points - (3 * OLD.home_team_win) - (1 * OLD.draw)
    WHERE team_id = OLD.home_team_id;

    -- Reverse away team standings
    UPDATE standings
    SET 
        played = played - 1,
        wins = wins - (OLD.away_team_win),
        losses = losses - (OLD.home_team_win),
        draws = draws - (OLD.draw),
        goals_for = goals_for - OLD.away_team_score,
        goals_against = goals_against - OLD.home_team_score,
        goal_difference = goal_difference - (OLD.away_team_score - OLD.home_team_score),
        points = points - (3 * OLD.away_team_win) - (1 * OLD.draw)
    WHERE team_id = OLD.away_team_id;
END;
"""

# Function to execute the trigger creation
def execute_trigger_creation():
    try:
        # Establish database connection
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            cursor = connection.cursor()

            # Drop existing triggers if they exist
            cursor.execute("DROP TRIGGER IF EXISTS after_match_insert;")
            cursor.execute("DROP TRIGGER IF EXISTS after_match_update;")
            cursor.execute("DROP TRIGGER IF EXISTS after_match_delete;")

            # Execute the trigger creation statements
            print("Creating AFTER INSERT trigger...")
            cursor.execute(trigger_after_insert)
            print("AFTER INSERT trigger created successfully!")

            print("Creating AFTER UPDATE trigger...")
            cursor.execute(trigger_after_update)
            print("AFTER UPDATE trigger created successfully!")

            print("Creating AFTER DELETE trigger...")
            cursor.execute(trigger_after_delete)
            print("AFTER DELETE trigger created successfully!")

            # Commit the changes
            connection.commit()

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")

# Run the function
if __name__ == "__main__":
    execute_trigger_creation()
