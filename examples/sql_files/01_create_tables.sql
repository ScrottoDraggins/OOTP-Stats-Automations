-- Example SQL file 1: Create tables
-- This file demonstrates table creation

CREATE TABLE IF NOT EXISTS teams (
    team_id INT PRIMARY KEY AUTO_INCREMENT,
    team_name VARCHAR(100) NOT NULL,
    city VARCHAR(100),
    founded_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS players (
    player_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    team_id INT,
    position VARCHAR(20),
    jersey_number INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

CREATE TABLE IF NOT EXISTS game_stats (
    stat_id INT PRIMARY KEY AUTO_INCREMENT,
    player_id INT NOT NULL,
    game_date DATE NOT NULL,
    at_bats INT DEFAULT 0,
    hits INT DEFAULT 0,
    runs INT DEFAULT 0,
    rbis INT DEFAULT 0,
    home_runs INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);
