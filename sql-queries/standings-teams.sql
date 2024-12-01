-- Hakan Çetinkaya
-- 150200114
-- 02.11.2024

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
    point_adjustment INT NOT NULL DEFAULT 0

    -- FOREIGN KEY (team_name) REFERENCES teams(team_name),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE teams (
    key_id INT AUTO_INCREMENT UNIQUE PRIMARY KEY,
    team_id VARCHAR(20) NOT NULL UNIQUE,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    former_team_names VARCHAR(255),
    current BOOLEAN NOT NULL,  -- Maybe they are integer I check it when I upload my data set as csv file.
    former BOOLEAN NOT NULL,
    defunct BOOLEAN NOT NULL,
    first_appearance INT NOT NULL
);

-- SELECT * FROM teams;
-- SELECT * FROM standings;
