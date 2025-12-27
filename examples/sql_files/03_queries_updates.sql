-- Example SQL file 3: Query and update data
-- This file demonstrates queries and updates

-- Update a player's team
UPDATE players 
SET team_id = 2 
WHERE first_name = 'Mookie' AND last_name = 'Betts';

-- Add an index for faster queries
CREATE INDEX idx_game_date ON game_stats(game_date);

-- Create a view for player statistics
CREATE OR REPLACE VIEW player_season_stats AS
SELECT 
    p.player_id,
    p.first_name,
    p.last_name,
    t.team_name,
    COUNT(gs.stat_id) AS games_played,
    SUM(gs.at_bats) AS total_at_bats,
    SUM(gs.hits) AS total_hits,
    SUM(gs.runs) AS total_runs,
    SUM(gs.rbis) AS total_rbis,
    SUM(gs.home_runs) AS total_home_runs,
    ROUND(SUM(gs.hits) / SUM(gs.at_bats), 3) AS batting_average
FROM players p
LEFT JOIN teams t ON p.team_id = t.team_id
LEFT JOIN game_stats gs ON p.player_id = gs.player_id
GROUP BY p.player_id, p.first_name, p.last_name, t.team_name;
