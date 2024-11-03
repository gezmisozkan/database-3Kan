-- Özkan Gezmiş
-- 150200033

-- create database 3kan;
show databases;
use 3kan;
show tables;

create table matches(
    key_id INT PRIMARY KEY,
    season_id VARCHAR(20) NOT NULL,
    season YEAR NOT NULL,
    tier INT NOT NULL CHECK (tier BETWEEN 1 AND 4),
    division VARCHAR(50) NOT NULL,
    subdivision VARCHAR(50) DEFAULT 'None',
    match_id VARCHAR(20) UNIQUE NOT NULL,
    match_name VARCHAR(100),
    home_team_id VARCHAR(20) NOT NULL,
    home_team_name VARCHAR(100) NOT NULL,
    away_team_id VARCHAR(20) NOT NULL,
    away_team_name VARCHAR(100) NOT NULL,
    score VARCHAR(5),
    home_team_score INT,
    away_team_score INT,
    home_team_score_margin INT,
    away_team_score_margin INT,
    result ENUM('home team win', 'away team win', 'draw') NOT NULL,
    home_team_win BOOLEAN NOT NULL,
    away_team_win BOOLEAN NOT NULL,
    draw BOOLEAN NOT NULL,
    
--    FOREIGN KEY (season_id) REFERENCES seasons(season_id),
--    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
--    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    
    CHECK (home_team_win + away_team_win + draw = 1),
    CHECK (home_team_score_margin = -away_team_score_margin),
    CHECK (season_id REGEXP '^S-[0-9]{4}-[0-9]+(-[A-Z])?$'),
    CHECK (match_id REGEXP '^M-[0-9]{4}-[0-9]+(-[A-Z])?-[0-9]{3}$')
);

CREATE TABLE appearances (
    key_id INT PRIMARY KEY,
    season_id VARCHAR(20) NOT NULL,
    season YEAR NOT NULL,
    tier INT NOT NULL CHECK (tier BETWEEN 1 AND 4),
    division VARCHAR(50) NOT NULL,
    subdivision VARCHAR(50) DEFAULT 'None',
    match_id VARCHAR(20) NOT NULL,
    match_name VARCHAR(100),
    team_id VARCHAR(20) NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    opponent_id VARCHAR(20) NOT NULL,
    opponent_name VARCHAR(100) NOT NULL,
    home_team BOOLEAN NOT NULL,
    away_team BOOLEAN NOT NULL,
    goals_for INT DEFAULT 0,
    goals_against INT DEFAULT 0,
    goal_difference INT GENERATED ALWAYS AS (goals_for - goals_against) STORED,
    result ENUM('win', 'lose', 'draw') NOT NULL,
    win BOOLEAN NOT NULL,
    lose BOOLEAN NOT NULL,
    draw BOOLEAN NOT NULL,
    points INT DEFAULT 0,

--    FOREIGN KEY (season_id) REFERENCES seasons(season_id),
--    FOREIGN KEY (match_id) REFERENCES matches(match_id),
--    FOREIGN KEY (team_id) REFERENCES teams(team_id),
--    FOREIGN KEY (opponent_id) REFERENCES teams(team_id),
    
	CHECK (win + lose + draw = 1),
    CHECK (home_team + away_team = 1)
);

-- show tables;
-- describe matches;