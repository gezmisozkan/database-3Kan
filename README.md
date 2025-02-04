# 3-KanDB - A Comprehensive Football Database

## Overview

3-KanDB is a Flask-based web application that allows users to explore, manage, and analyze football data, including teams, matches, standings, and seasons. This project aims to provide a structured and efficient way to store and retrieve football statistics using a MySQL database.

## Features

- **User Authentication**: Sign-up, login, and logout functionality.
- **Teams Management**: View, search, and manage football teams.
- **Match Tracking**: Insert, update, and view match details.
- **Season Overview**: View and analyze past football seasons.
- **Standings Management**: Track team rankings within different seasons and divisions.
- **Comments & Discussions**: Users can comment on matches and teams.
- **Admin Panel**: Manage teams, matches, seasons, standings, and comments.

---

## **Project Structure**

```
/FootballDB
│── /football/                # Contains CSV files with football data
│── /sql-queries/             # MySQL schema and queries
│── /website/                 # Application logic and views
│   │── auth.py               # Authentication and user management
│   │── views.py              # Application routes and functionalities
│   │── static/               # Static files for website
│   │── templates/            # HTML templates for the website
│── /utils/                   # Contains database scripts
│   │── build_database.py     # Builds the database schema
│   │── insert_database.py    # Inserts initial data into the database
│── main.py                   # Main entry point for the application
│── README.md                 # Documentation
```

---

## **Installation & Setup**

### **1. Create MySQL User**

Before proceeding, create a MySQL user with the following credentials:

```
Username: root
Password: 1234
```

### **2. Clone the repository**

```sh
git clone https://github.com/gezmisozkan/database-3Kan.git
cd database-3Kan
```

### **3. Install Dependencies**

FootballDB requires Python 3 and pip. Install dependencies using:

```sh
pip install -r requirements.txt
```

### **4. Set up the MySQL Database**

- Ensure the MySQL user (`root`, `1234`) is created.
- Run the database setup scripts:

```sh
python utils/build_database.py
python utils/insert_database.py
```

### **5. Run the Application**

```sh
python main.py
```

- The application will be available at `http://127.0.0.1:5000/`.

## **Usage**

- **User Actions**
  - Sign up or log in to interact with the database.
  - Browse teams and match details.
  - Add comments on matches or teams.
- **Admin Actions**
  - Add or update match results.
  - Manage teams, matches, seasons, and standings.
  - Delete inappropriate comments.

---

## **Contributors**

- **Özkan Gezmiş** - Data Specialist and Backend Developer
- **Hakan Çetinkaya** - Full Stack Developer
- **Okan Zagor A.** - Developer and System Analyst

---

## **License**

This project is open-source and available under the MIT License.

