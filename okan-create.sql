CREATE TABLE seasons (
    key_id INT PRIMARY KEY,
    season_id VARCHAR(20) UNIQUE NOT NULL,
    season YEAR NOT NULL,
    tier INT NOT NULL CHECK (tier BETWEEN 1 AND 4),
    division VARCHAR(50) NOT NULL,
    subdivision VARCHAR(50) DEFAULT 'None',
    winner VARCHAR(100),
    count_teams INT CHECK (count_teams > 0),
    
	CHECK (season_id REGEXP '^S-[0-9]{4}-[0-9]+(-[A-Z])?$')
);
