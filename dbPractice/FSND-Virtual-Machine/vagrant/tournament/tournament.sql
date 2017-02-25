-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

CREATE TABLE players (id SERIAL PRIMARY KEY,
                      name TEXT);

CREATE TABLE matches (id SERIAL PRIMARY KEY,
                      winner INTEGER REFERENCES players(id),
                      loser INTEGER REFERENCES players(id));

CREATE OR REPLACE VIEW num_wins AS
    SELECT players.id AS id, COUNT(matches.winner) AS wins
        FROM players LEFT JOIN matches ON players.id = matches.winner
        GROUP BY players.id;

CREATE OR REPLACE VIEW num_losses AS
    SELECT players.id AS id, COUNT(matches.loser) AS losses
        FROM players LEFT JOIN matches ON players.id = matches.loser
        GROUP BY players.id
