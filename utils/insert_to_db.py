import os
import pandas as pd
import mysql.connector
from werkzeug.security import generate_password_hash

# Database connection details
user = 'root'
password = '1234'
host = 'localhost'
database = '3kan'

# Connect to MySQL database
db = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
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
        
        # Read the CSV file into a DataFrame
        file_path = os.path.join(csv_directory, filename)

       # Adjust this dictionary to specify dtypes for each column that might have issues
        dtype_mapping = {
            'appearances.csv': {'column_5': 'str'},
            'matches.csv': {'column_5': 'str'},
            'seasons.csv': {'column_5': 'str'},
            'standings.csv': {'column_5': 'str'},
            'teams.csv': {'column_5': 'int'}
        }
        
        try:
            if filename in dtype_mapping:
                df = pd.read_csv(file_path, dtype=dtype_mapping[filename])
            else:
                df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
        
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