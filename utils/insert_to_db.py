import pandas as pd
import mysql.connector
import os
from werkzeug.security import generate_password_hash
from build_database import Config

# Database connection details
db = mysql.connector.connect(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME
)

# Use a single cursor for all queries
cursor = db.cursor()

# Part 1: Insert Admin User
email = 'admin@admin.com'
password = 'admin1234'
hashed_password = generate_password_hash(password, method='scrypt')
full_name = 'Admin User'
role = 'admin'

try:
    cursor.execute("""
        INSERT INTO User (email, password, full_name, role) 
        VALUES (%s, %s, %s, %s)
    """, (email, hashed_password, full_name, role))
    db.commit()
    print(f'Admin user {email} created successfully!')
except mysql.connector.Error as e:
    print(f"Error inserting admin user: {e}")

# Part 2: Insert CSV Data into Database
csv_directory = 'football/simpified_csv'

# Loop through each CSV file in the directory
for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        # Get the table name by removing '.csv' from the filename
        table_name = filename.split('.csv')[0]
        
        # Read the CSV file into a DataFrame with specified data types
        file_path = os.path.join(csv_directory, filename)
        
        if filename == 'appearances.csv':
            dtype = {
                'key_id': int,
                'season_id': str,
                'season': str,
                'tier': int,
                'division': str,
                'subdivision': str,
                'match_id': str,
                'match_name': str,
                'team_id': str,
                'team_name': str,
                'opponent_id': str,
                'opponent_name': str,
                'home_team': bool,
                'away_team': bool,
                'goals_for': int,
                'goals_against': int,
                'goal_difference': int,
                'result': str,
                'win': bool,
                'lose': bool,
                'draw': bool,
                'points': int
            }
            df = pd.read_csv(file_path, dtype=dtype, na_values=['nan', 'NaN'])
            df = df.fillna({
                'subdivision': 'None',
                'match_name': '',
                'goal_difference': 0,
                'points': 0,
                'home_team': False,
                'away_team': False,
                'win': False,
                'lose': False,
                'draw': False
            })
        elif filename == 'matches.csv':
            dtype = {
                'key_id': int,
                'season_id': str,
                'season': str,
                'tier': int,
                'division': str,
                'subdivision': str,
                'match_id': str,
                'match_name': str,
                'home_team_id': str,
                'home_team_name': str,
                'away_team_id': str,
                'away_team_name': str,
                'score': str,
                'home_team_score': int,
                'away_team_score': int,
                'home_team_score_margin': int,
                'away_team_score_margin': int,
                'result': str,
                'home_team_win': bool,
                'away_team_win': bool,
                'draw': bool
            }
            df = pd.read_csv(file_path, dtype=dtype, na_values=['nan', 'NaN'])
            df = df.fillna({
                'subdivision': 'None',
                'match_name': '',
                'score': '',
                'home_team_score': 0,
                'away_team_score': 0,
                'home_team_score_margin': 0,
                'away_team_score_margin': 0,
                'home_team_win': False,
                'away_team_win': False,
                'draw': False
            })
        elif filename == 'seasons.csv':
            dtype = {
                'key_id': int,
                'season_id': str,
                'season': str,
                'tier': int,
                'division': str,
                'subdivision': str,
                'winner': str,
                'count_teams': int
            }
            df = pd.read_csv(file_path, dtype=dtype, na_values=['nan', 'NaN'])
            df = df.fillna({
                'subdivision': 'None',
                'winner': ''
            })
        elif filename == 'standings.csv':
            dtype = {
                'key_id': int,
                'season_id': str,
                'season': int,
                'tier': int,
                'division': str,
                'subdivision': str,
                'position': int,
                'team_id': str,
                'team_name': str,
                'played': int,
                'wins': int,
                'draws': int,
                'losses': int,
                'goals_for': int,
                'goals_against': int,
                'goal_difference': int,
                'points': int,
                'point_adjustment': int
            }
            df = pd.read_csv(file_path, dtype=dtype, na_values=['nan', 'NaN'])
            df = df.fillna({
                'subdivision': 'None'
            })
        elif filename == 'teams.csv':
            dtype = {
                'key_id': int,
                'team_id': str,
                'team_name': str,
                'former_team_names': str,
                'current': bool,
                'former': bool,
                'defunct': bool,
                'first_appearance': int
            }
            df = pd.read_csv(file_path, dtype=dtype, na_values=['nan', 'NaN'])
            df = df.fillna({
                'former_team_names': ''
            })
        else:
            df = pd.read_csv(file_path)

        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Clear existing data in the table
            cursor.execute(f"TRUNCATE TABLE {table_name}")
            
            # Insert new data from the DataFrame into the table
            for index, row in df.iterrows():
                columns = ', '.join(df.columns)
                values = ', '.join(['%s'] * len(row))
                insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
                cursor.execute(insert_query, tuple(row))

            db.commit()
            print(f"Table '{table_name}' cleared and new data inserted from {filename} successfully.")
        except mysql.connector.Error as e:
            print(f"An error occurred while inserting data from {filename} into table '{table_name}': {e}")
        finally:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# Close the cursor and the database connection at the end of the script
cursor.close()
db.close()