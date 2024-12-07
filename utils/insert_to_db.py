import os
import pandas as pd
import mysql.connector

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

# Directory containing your CSV files
csv_directory = 'football/simpified_csv'

# Loop through each CSV file in the directory
for filename in os.listdir(csv_directory):
    if filename.endswith('.csv'):
        # Get the table name by removing '.csv' from the filename
        table_name = filename.split('.csv')[0]
        
        # Read the CSV file into a DataFrame
        file_path = os.path.join(csv_directory, filename)
        df = pd.read_csv(file_path)
        
        cursor = db.cursor()
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
            cursor.close()
        
db.close()
