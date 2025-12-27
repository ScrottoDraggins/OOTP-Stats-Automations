-- Example SQL file 2: Insert sample data
-- This file demonstrates data insertion

-- Insert teams
INSERT INTO teams (team_name, city, founded_year) VALUES
    ('Red Sox', 'Boston', 1901),
    ('Yankees', 'New York', 1903),
    ('Cubs', 'Chicago', 1876),
    ('Dodgers', 'Los Angeles', 1883);

-- Insert players
INSERT INTO players (first_name, last_name, team_id, position, jersey_number) VALUES
    ('Mike', 'Trout', 1, 'OF', 27),
    ('Aaron', 'Judge', 2, 'OF', 99),
    ('Kris', 'Bryant', 3, '3B', 17),
    ('Mookie', 'Betts', 4, 'OF', 50);

-- Insert game stats
INSERT INTO game_stats (player_id, game_date, at_bats, hits, runs, rbis, home_runs) VALUES
    (1, '2024-01-15', 4, 2, 1, 2, 1),
    (1, '2024-01-16', 5, 3, 2, 3, 0),
    (2, '2024-01-15', 4, 1, 1, 1, 1),
    (2, '2024-01-16', 3, 2, 1, 2, 0),
    (3, '2024-01-15', 4, 2, 0, 1, 0),
    (4, '2024-01-15', 5, 4, 3, 4, 2);
