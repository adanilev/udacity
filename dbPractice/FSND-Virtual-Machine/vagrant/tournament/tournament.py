#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM matches")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT COUNT(*) as num_players FROM players")
    result = c.fetchone()[0]
    DB.close()
    return result


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO players (name) VALUES (%s)", (bleach.clean(name),))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    # I would love to figure out a cleaner way to do the two joins. Had trouble
    # matching players.id to the 2 columns in matches. After a long battle, this
    # worked and I have accepted the ugly win, for now.
    c.execute("""
        SELECT
            players.id,
            players.name,
            winners.wins,
            winners.wins + losers.losses
        FROM players
            LEFT JOIN (SELECT players.id AS id, COUNT(matches.winner) AS wins FROM players LEFT JOIN matches ON players.id = matches.winner GROUP BY players.id) AS winners
                ON players.id = winners.id
            LEFT JOIN (SELECT players.id AS id, COUNT(matches.loser) AS losses FROM players LEFT JOIN matches ON players.id = matches.loser GROUP BY players.id) AS losers
                ON players.id = losers.id
        ORDER BY winners.wins DESC;
    """)
    result = c.fetchall()
    DB.close()
    return result


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO matches (winner,loser) VALUES (%s,%s)",
              (winner,loser))
    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # Using the ranking we figure out in playerStandings
    player_list = playerStandings()
    i = 0
    result = []
    # Go through and pair people that are next to one another in the rankings
    # Or am I supposed to be using a query to get the result as a table?
    while i < len(player_list):
        t = (player_list[i][0], player_list[i][1],
             player_list[i+1][0], player_list[i+1][1])
        result.append(t)
        i += 2
    return result
