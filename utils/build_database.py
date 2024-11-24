import mysql.connector
from mysql.connector import errorcode
import os

# Database connection configuration
config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost'
}

# Name of the database to drop and recreate
DATABASE_NAME = '3kan'

# Path to your folder containing the additional .sql files
sql_files_directory = 'sql-queries'

def rebuild_database(config, database_name, sql_files_directory):
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Drop the existing database if it exists
        cursor.execute(f"DROP DATABASE IF EXISTS {database_name};")
        print(f"Dropped database: {database_name}")

        # Create a new database
        cursor.execute(f"CREATE DATABASE {database_name};")
        print(f"Created database: {database_name}")

        # Use the newly created database
        cursor.execute(f"USE {database_name};")

        # Execute each .sql file in the directory
        for filename in sorted(os.listdir(sql_files_directory)):
            if filename.endswith('.sql'):
                file_path = os.path.join(sql_files_directory, filename)
                print(f"Executing {filename}...")

                with open(file_path, 'r') as file:
                    sql_commands = file.read()

                    # Split commands by semicolon and execute each
                    for command in sql_commands.split(';'):
                        if command.strip():  # Skip empty commands
                            try:
                                cursor.execute(command)
                                print(f"Executed command: {command.strip()[:50]}...")
                            except mysql.connector.Error as err:
                                print(f"Error executing command: {err}")

        connection.commit()
        print("Database rebuilt successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied: Check your username and password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        else:
            print(err)
    finally:
        cursor.close()
        connection.close()

# Call the rebuild function
rebuild_database(config, DATABASE_NAME, sql_files_directory)