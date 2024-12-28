# **Database-3Kan**

A web application that uses a MySQL database for managing football team and match data. It uses the MySQL database for user authentication and comment property as well.  

---

## **Getting Started**

Follow these steps to set up and use the project on your local machine:

---

### **Clone the Repository**

Clone the repository to your local machine:

```bash
git clone https://github.com/gezmisozkan/database-3Kan.git
cd database-3Kan
```

### Install the necessary Python packages using pip:
```bash
pip install -r requirements.txt
```

### To set up the MySQL and SQLite databases:
Ensure you have MySQL installed and running on your system.
#### Build MySQL Database
Run the script in the utils directory to build the database:
This script will drop the old database (if any), create a new one, and define the schema.
```bash
python utils/build_database.py
```
#### Insert Data into MySQL
Use the script in the utils directory to insert data into the MySQL database:
Ensure your .csv files for data insertion are in the appropriate directory (specified in the script).
```bash
python utils/insert_to_db.py
```

### Start the Application
Run the main script to start the web application:
This will start the Flask server and build the website. Navigate to: http://127.0.0.1:5000/
```bash
python main.py
```

### **Features**

- **User Authentication**:
  - Users can sign up and log in using MySQL for authentication.
- **Team Management**:
  - View and manage football teams and matches using MySQL.
- **Interactive Interface**:
  - Select a team and view match results.

---

### **Folder Structure**

- **`utils`**: Contains scripts for building and inserting data into the database.
  - `build_database.py`: Script for creating and configuring the database.
  - `insert_to_db.py`: Script for inserting data into the MySQL database.
- **`website`**: Contains the web application code.
  - `auth.py`: Handles user authentication.
  - `views.py`: Defines routes and logic for the website.
  - `models.py`: Contains database models.
  - `templates/`: HTML templates for rendering the web pages.

## Screenshots for website

You can see the some main pages in our website by looking screenshots named home_page.png, matches_page.png,
seasons_page.png,
standings_page.png teams_page.png