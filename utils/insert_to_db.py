import os
import pandas as pd
from sqlalchemy import create_engine

# Database connection details
user = 'root'
password = '1234'
host = 'localhost'
database = '3kan'

# Create a connection engine
engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

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
        
        # Insert data into the corresponding table in the MySQL database
        try:
            # Delete existing table data and replace it with new rows
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
            print(f"Table '{table_name}' cleared and new data inserted from {filename} successfully.")
        except Exception as e:
            print(f"An error occurred while inserting data from {filename} into table '{table_name}': {e}")
