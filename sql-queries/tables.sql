CREATE TABLE seasons (
    key_id INT PRIMARY KEY,
    season_id VARCHAR(20) UNIQUE NOT NULL,
    season CHAR(4) NOT NULL,
    tier INT NOT NULL CHECK (tier BETWEEN 1 AND 4),
    division VARCHAR(50) NOT NULL,
    subdivision VARCHAR(50) DEFAULT 'None',
    winner VARCHAR(100),
    count_teams INT CHECK (count_teams > 0),
    
	CHECK (season_id REGEXP '^S-[0-9]{4}-[0-9]+(-[A-Z])?$')
);


CREATE TABLE teams (
    key_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
    team_id VARCHAR(20) NOT NULL UNIQUE,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    former_team_names VARCHAR(255),
    current BOOLEAN NOT NULL,
    former BOOLEAN NOT NULL,
    defunct BOOLEAN NOT NULL,
    first_appearance INT NOT NULL
);


CREATE TABLE standings (
    key_id INT AUTO_INCREMENT PRIMARY KEY,
    season_id VARCHAR(20) NOT NULL,
    season INT NOT NULL,
    tier INT NOT NULL,
    division VARCHAR(100) NOT NULL,
    subdivision VARCHAR(100) DEFAULT 'None',
    position INT NOT NULL,
    team_id VARCHAR(20) NOT NULL,
    team_name VARCHAR(100) NOT NULL,
    played INT NOT NULL,
    wins INT NOT NULL,
    draws INT NOT NULL,
    losses INT NOT NULL,
    goals_for INT NOT NULL,
    goals_against INT NOT NULL,
    goal_difference INT NOT NULL,
    points INT NOT NULL,
    point_adjustment INT NOT NULL DEFAULT 0,

    -- FOREIGN KEY (team_name) REFERENCES teams(team_name),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);


create table matches(
    key_id INT PRIMARY KEY,
    season_id VARCHAR(20) NOT NULL,
    season CHAR(4) NOT NULL,
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
    
    -- FOREIGN KEY (season_id) REFERENCES seasons(season_id),
	
    -- FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    -- FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    
    CHECK (home_team_win + away_team_win + draw = 1),
    CHECK (home_team_score_margin = -away_team_score_margin),
    CHECK (season_id REGEXP '^S-[0-9]{4}-[0-9]+(-[A-Z])?$'),
    CHECK (match_id REGEXP '^M-[0-9]{4}-[0-9]+(-[A-Z])?-[0-9]{3}$')
);

CREATE TABLE appearances (
    key_id INT PRIMARY KEY,
    season_id VARCHAR(20) NOT NULL,
    season CHAR(4) NOT NULL,
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
--    goal_difference INT GENERATED ALWAYS AS (goals_for - goals_against) STORED,
    goal_difference INT,
    result ENUM('win', 'lose', 'draw') NOT NULL,
    win BOOLEAN NOT NULL,
    lose BOOLEAN NOT NULL,
    draw BOOLEAN NOT NULL,
    points INT DEFAULT 0,

    -- FOREIGN KEY (match_id) REFERENCES matches(match_id),
	
    -- FOREIGN KEY (season_id) REFERENCES seasons(season_id),
	
    -- FOREIGN KEY (team_id) REFERENCES teams(team_id),
    -- FOREIGN KEY (opponent_id) REFERENCES teams(team_id),
	
    CHECK (win + lose + draw = 1),
    CHECK (home_team + away_team = 1)
);

CREATE INDEX season_id_index
 ON seasons(season_id);

CREATE INDEX team_id_index
 ON teams(team_id );
